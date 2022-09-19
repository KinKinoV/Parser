from bs4 import BeautifulSoup, NavigableString, ResultSet, Tag
from time import sleep
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import gc
import keyboard
import parseconfigs
import re
import os
import requests
import sqlite3

FIRST_RESULTS = 'results\\usernames.txt'

# PARSER SETTINGS FOR PARSE
# Pagination step in case PAGINATION_CASE == 'C'
FORUM_STEP = int()
THREAD_STEP = int()
# Flag for special word to add to FORUM if needed
S_WORD_FLAG = False
# Position of a thread's link in thread's tag (in case if there are more than one link)
THREAD_LINK_POS = int()
# Pagination kind on forum and it's template to add to the end of needed link
PAGINATION_CASE = str()
PAGINATAION_TEMPLATE = str()
# Flag to parse forum using selenium in case requests are not working (404, 502, etc. errors)
BOT_PROTECTION = False
# In case forum throws 503 -- Service Unavaible error, you need to make delay between requests
PAGE_LOAD_DELAY = float()
# Tags to use in scraping
SITE_TAGS = None
# MAIN link to the forum
FORUM = str()
# Selenium driver to use (scripts uses geckodriver for FireFox)
DRIVER = None

# Fetched from the DB
# Words to NOT to write to result file
BANNED_EXCEPTIONS = []
# If any in thread's message, start searching for needed data
KEY_WORDS = []

DEBUG_MODE = False

def start():
    global SITE_TAGS
    forum_soft = input('''Enter software name on which forum is working
    Possible variants:
        1.Xceref
        2.phpBB
        3.Other\n
    Enter name or number: ''')
    if forum_soft == '1' or forum_soft == 'Xceref':
        SITE_TAGS = parseconfigs.Xceref()
    if forum_soft == '2' or forum_soft == 'phpBB':
        SITE_TAGS = parseconfigs.phpBB()
    if forum_soft == '3' or forum_soft == 'Other':
        try:
            print('\n\nPlease, go to the http://localhost:5000/ and enter all needed data.\nAfter entering, press Ctrl+C in this window.')
            os.system("py server.py")
        except KeyboardInterrupt:
            print('Server stoped!')
            pass
        SITE_TAGS = parseconfigs.OtherSoft()
    
    parse()

# Writes found telegram tags/names or other key words to the file
def find_names(forum_texts:list)->None:
    total_found = 0  
    with open(FIRST_RESULTS, 'a', encoding="utf-8") as file:
        for tag in forum_texts:
            for word in KEY_WORDS:
                if word in tag.text:
                    # Accepted characters: A-z (case-insensitive), 0-9 and underscores. Length: 5-32 characters.
                    # In re.findall() RegEx !MUST! be written in format: r"<*Your RegEx*>". Using re.compile() breaks script
                    found_data =  re.findall(r".\B(?=\w{5,32}\b)[a-zA-Z0-9]+(?:_[a-zA-Z0-9]+)*", tag.text.split(word)[1])
                    for data in found_data:
                        total_found += 1
                        if not (data in BANNED_EXCEPTIONS):
                            file.write(data + '\n')
    print(f'Found {total_found} nicknames.')

# Scrapes text on thread's page
def scrape_page(forum_posts:ResultSet)->None:
    text = []
    for post in forum_posts:
        text.append(post.find(SITE_TAGS.message_tag, SITE_TAGS.message_parameter))
    find_names(text)

# Scrapes all pages in a thread
def scrape_thread(current_thread:str, s:requests.Session)->None:
    print(f'Scraping {current_thread}')

    html_text = str()
    if BOT_PROTECTION:
        DRIVER.get(current_thread)
        sleep(PAGE_LOAD_DELAY)
        html_text = DRIVER.page_source
    else:
        html_text = s.get(current_thread).text
        sleep(PAGE_LOAD_DELAY)
    
    soup = BeautifulSoup(html_text, 'html.parser')
    # Checking for pagination
    check_pagination = soup.find(SITE_TAGS.pagination_tag, SITE_TAGS.pagination_parameter)
    # Finding all posts for case where there are only one page in thread
    forum_posts = soup.find_all(SITE_TAGS.thread_post_tag, SITE_TAGS.thread_post_parameter)
    if check_pagination:
        scrape_page(forum_posts)
        check_same_ = Tag|NavigableString|None
        if PAGINATION_CASE == 'I':
            for i in range(2,5000):
                html_text = str()
                if BOT_PROTECTION:
                    DRIVER.get(current_thread+PAGINATAION_TEMPLATE.format(i))
                    sleep(PAGE_LOAD_DELAY)
                    html_text = DRIVER.page_source
                else:
                    html_text = s.get(current_thread+PAGINATAION_TEMPLATE.format(i)).text
                    sleep(PAGE_LOAD_DELAY)
                thread_soup = BeautifulSoup(html_text, "html.parser")
                check_same = thread_soup.find('link', {'rel' : 'canonical'})
                if check_same_ == check_same:
                    break
                else:
                    check_same_ = check_same 
                    forum_posts = thread_soup.find_all(SITE_TAGS.thread_post_tag, SITE_TAGS.thread_post_parameter)
                    scrape_page(forum_posts)
        if PAGINATION_CASE == 'C':
            for i in range(THREAD_STEP, 50000, THREAD_STEP):
                html_text = str()
                if BOT_PROTECTION:
                    DRIVER.get(current_thread+PAGINATAION_TEMPLATE.format(i))
                    sleep(PAGE_LOAD_DELAY)
                    html_text = DRIVER.page_source
                else:
                    html_text = s.get(current_thread+PAGINATAION_TEMPLATE.format(i)).text
                    sleep(PAGE_LOAD_DELAY)
                thread_soup = BeautifulSoup(html_text, "html.parser")
                check_same = thread_soup.find('link', {'rel' : 'canonical'})
                if check_same_ == check_same:
                    break
                else:
                    check_same_ = check_same 
                    forum_posts = thread_soup.find_all(SITE_TAGS.thread_post_tag, SITE_TAGS.thread_post_parameter)
                    scrape_page(forum_posts)
    else:
        scrape_page(forum_posts)
    print("Succesfully scraped!\n")
    del(soup)
    del(check_pagination)
    del(forum_posts)
    gc.collect()

# Scraping BS of current forum page
def scrape_forum_page(s:requests.Session, forum_page:BeautifulSoup):
    thread_links = forum_page.find_all(SITE_TAGS.forum_threads_tag, SITE_TAGS.forum_threads_parameter)
    for tag in thread_links:
        a_tags = tag.findChildren('a')
        if THREAD_LINK_POS:
            if len(a_tags) == 1:
                if ('https://' in a_tags[0]["href"]) or ('http://' in a_tags[0]["href"]):
                    scrape_thread(f'{a_tags[0]["href"]}', s)
                else:
                    scrape_thread(f'{FORUM}{a_tags[0]["href"]}', s)
                
            if len(a_tags) >= THREAD_LINK_POS:
                if ('https://' in a_tags[THREAD_LINK_POS-1]["href"]) or ('http://' in a_tags[THREAD_LINK_POS-1]["href"]):
                    scrape_thread(f'{a_tags[THREAD_LINK_POS-1]["href"]}', s)
                else:
                    scrape_thread(f'{FORUM}{a_tags[THREAD_LINK_POS-1]["href"]}', s)
        else:
            if ('https://' in a_tags[0]["href"]) or ('http://' in a_tags[0]["href"]):
                scrape_thread(f'{a_tags[0]["href"]}', s)
            else:
                scrape_thread(f'{FORUM}{a_tags[0]["href"]}', s)

# Scraping all threads of the current forum
def scrape_forum(s:requests.Session, forum_url:str):
    print(f'\n\nScrapping {forum_url}...\n')
    html_form = str()
    if BOT_PROTECTION:
        DRIVER.get(forum_url)
        sleep(PAGE_LOAD_DELAY)
        html_form = DRIVER.page_source
    else:
        html_form = s.get(forum_url).text
        sleep(PAGE_LOAD_DELAY)
    soup = BeautifulSoup(html_form, "html.parser")
    # Checking for pagination of forum
    check_pagination = soup.find(SITE_TAGS.pagination_tag, SITE_TAGS.pagination_parameter)
    if check_pagination:
        scrape_forum_page(s, soup)
        print(f'{"-"*10}Scraped page 1 {"-"*10}\n')
        del(soup)
        gc.collect()
        check_same_ = Tag|NavigableString|None
        if PAGINATION_CASE == 'I':
            for i in range(2, 5000):
                # Creating soup of the current page
                forum_page = None
                if BOT_PROTECTION:
                    DRIVER.get(forum_url+PAGINATAION_TEMPLATE.format(i))
                    sleep(PAGE_LOAD_DELAY)
                    forum_page = BeautifulSoup(DRIVER.page_source, "html.parser")
                else:
                    forum_page = BeautifulSoup(s.get(forum_url+PAGINATAION_TEMPLATE.format(i)).text, "html.parser")
                    sleep(PAGE_LOAD_DELAY)
                # Checking if we are on the last page
                check_same = forum_page.find('link', {'rel' : 'canonical'})
                if check_same_ == check_same:
                    break
                else:
                    # We are not on the last page, remembering unique info about current page...
                    check_same_ = check_same
                    # ...and scraping it
                    scrape_forum_page(s, forum_page)
                    print(f'{"-"*10}Scraped page {i}{"-"*10}\n')
        if PAGINATION_CASE == 'C':
            page = 2
            for i in range(FORUM_STEP, 50000, FORUM_STEP):    
                # Creating soup of the current page
                forum_page = None
                if BOT_PROTECTION:
                    DRIVER.get(forum_url+PAGINATAION_TEMPLATE.format(i))
                    sleep(PAGE_LOAD_DELAY)
                    forum_page = BeautifulSoup(DRIVER.page_source, "html.parser")
                else:
                    forum_page = BeautifulSoup(s.get(forum_url+PAGINATAION_TEMPLATE.format(i)).text, "html.parser")
                    sleep(PAGE_LOAD_DELAY)
                # Checking if we are on the last page
                check_same = forum_page.find('link', {'rel' : 'canonical'})
                if check_same_ == check_same:
                    break
                else:
                    # We are not on the last page, remembering unique info about current page...
                    check_same_ = check_same
                    # ...and scraping it
                    scrape_forum_page(s, forum_page)
                    print(f'{"-"*10}Scraped page {page}{"-"*10}\n')
                    page += 1
    else:
        scrape_forum_page(s, soup)
    print(f'\n\nScraped {forum_url}!\a')

def scrape_setup(s:requests.Session)->bool:

    fetch_data()

    global FORUM_STEP, THREAD_STEP, S_WORD_FLAG, THREAD_LINK_POS
    global PAGINATION_CASE, PAGINATAION_TEMPLATE, BOT_PROTECTION
    global PAGE_LOAD_DELAY

    special_word = str()
    if SITE_TAGS.type_ == 'Other':
        # Getting special str() in case it's needed to succesfully load links
        if input('Do you need to add special words to base forum link to go to other threads? [Y] -- Yes, [N] -- No\n') == 'Y':
            special_word = input('Then enter this word: ')
            S_WORD_FLAG = True
        else:
            S_WORD_FLAG = False
            del(special_word)
            gc.collect()
        
        # Checkin pagination type of the forum
        PAGINATION_CASE = input('How pagination works on this forum? Just by incrementing value (adding 1,2,3,...,100 to something like "page" or "index") \
                or by counting post/threads (something like: ...&?start=15/30/45)?\n[I] -- Incrementing, [C] -- counting\n')
        if PAGINATION_CASE == 'C':
            print("You've chosen [C], please enter next data:")
            FORUM_STEP = int(input('Enter step for pagination for pages with threads(in phpBB usually 50): '))
            THREAD_STEP = int(input('Enter step for pagination for threads with posts(in phpBB usually 15): '))
        PAGINATAION_TEMPLATE =  input("Please, enter template that is added to the end of url with {} where page number is placed: ")

        if input("Does forum has special prefixes(post tags) that are links too? [Y]--Yes [N]--No\n") == 'Y':
            # Getting position of <a> tag in forum HTML for (!)threads(!) links
            THREAD_LINK_POS = int(input("Enter position of a thread's link in main page's HTML: "))

        if input("Does forum has bot protection (can load pages only through browser)? [Y]--Yes [N]--No\n") == 'Y':
            BOT_PROTECTION = True
        else:
            BOT_PROTECTION = False
            DRIVER.close()

        if input("Does site need delay between page loads? [Y]--Yes [N]--No\n") == 'Y':
            PAGE_LOAD_DELAY = float(input("Enter delay in seconds: "))
        else:
            PAGE_LOAD_DELAY = 0
    else:
        if SITE_TAGS.pagination_case == 'C':
            PAGINATION_CASE == 'C'
            FORUM_STEP = SITE_TAGS.forum_step
            THREAD_STEP = SITE_TAGS.thread_step
        if SITE_TAGS.pagination_case == 'I':
            PAGINATION_CASE = 'I'
        if SITE_TAGS.s_word_flag:
            S_WORD_FLAG = True
            special_word = SITE_TAGS.s_word
        THREAD_LINK_POS = SITE_TAGS.thread_link_pos
        PAGINATAION_TEMPLATE = SITE_TAGS.pagination_template
        BOT_PROTECTION = SITE_TAGS.bot_protection
        PAGE_LOAD_DELAY = SITE_TAGS.page_load_delay
        
    to_parse = []
    # Starting to scrape forum using links provided in "txt/to_parse.txt"
    for line in open('data\\to_parse.txt', 'r'):
        to_parse.append(str(line.rstrip()))

    forum_url = str()
    for link in to_parse:
        if S_WORD_FLAG:
            forum_url = FORUM + special_word + link
        else:
            forum_url = FORUM + link
        scrape_forum(s, forum_url)
    
    return False
        
def fetch_data():
    global BANNED_EXCEPTIONS, KEY_WORDS

    conn = sqlite3.connect('parser.db')
    print('Succesfuly opened DB!')
    # Name of file to save results to
    # Pulling banned words from the database

    cursor = conn.execute("SELECT word FROM banned_words")
    for row in cursor:
        BANNED_EXCEPTIONS.append(row[0])
    print('Fetched banned words!')
    # Pulling key words from the database

    cursor = conn.execute("SELECT word FROM key_words")
    for row in cursor:
        KEY_WORDS.append(row[0])
    print('Fetched key words!')
    conn.close()

def copy_cookies(s:requests.Session):
    for cookie in DRIVER.get_cookies():
            c = {cookie['name']: cookie['value']}
            s.cookies.update(c)
    print("Cookies coppied successfully!")

def parse()->None:
    global FORUM, DRIVER

    options_ = Options()
    options_.page_load_strategy = 'eager'
    s = Service("geckodriver.exe")
    DRIVER = webdriver.Firefox(service=s, options=options_)

    FORUM = input('Enter main link to the forum: ')
    # Получаю куки-файлы из селениума и передаю их скрипту для
    # удачных реквестов страниц 
    DRIVER.get(f"{FORUM}")
    s = requests.Session()
    if input('Is logged in user required to parse forum? [Y] -- Yes, [N] -- No\n') == 'Y':
        print('Please, go to the login page of the forum and complete signing in.\n')
        if input('Have you completed login? Enter [Y] to continue: ') == 'Y':
            copy_cookies(s)
        else:
            print("You didn't enter Y!")
            return
    else:
        copy_cookies(s)
    
    # Цикл для ручного запуска парсинга форума или остановки скрипта
    A = True
    while A:
        if keyboard.is_pressed("S"):
            A = scrape_setup(s)
        if keyboard.is_pressed("Q"):
            print("Stopping script!")
            try:
                DRIVER.close()
            except Exception as e:
                print(e)
                pass
            A = False
    
if __name__ == '__main__':
    start()