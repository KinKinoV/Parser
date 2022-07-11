from bs4 import BeautifulSoup, NavigableString, ResultSet, Tag
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import gc
import keyboard
import re
import requests
import sqlite3

FORUM_STEP = int()
THREAD_STEP = int()
S_WORD_FLAG = False
THREAD_LINK_POS = int()
PAGINATION_CASE = str()
PAGINATAION_TEMPLATE = str()
BOT_PROTECTION = False

print('Please, enter all needed information about forum HTML:\n')
class OtherSoft:
    message_tag = input("Enter tag where a post's text is: ")
    message_parameter = {}
    for i in range(int(input(f'How many parameters in a {message_tag} tag? '))):
        if input("Do you need regular expressions for this tag? ") == 'Y':
            message_parameter[input(f'Enter parameter {i+1} name: ')] = re.compile(input(f'Enter parameter {i+1} value: '))
        else:
            message_parameter[input(f'Enter parameter {i+1} name: ')] = (input(f'Enter parameter {i+1} value: '))
    #input("Enter class where a post's text is: ")
    pagination_tag = input("Enter tag of the pagination module: ")
    pagination_parameter = {}
    for i in range(int(input(f'How many parameters in a {pagination_tag} tag? '))):
        if input("Do you need regular expressions for this tag? ") == 'Y':
            pagination_parameter[input(f'Enter parameter {i+1} name: ')] = re.compile(input(f'Enter parameter {i+1} value: '))
        else:
            pagination_parameter[input(f'Enter parameter {i+1} name: ')] = input(f'Enter parameter {i+1} value: ')
    thread_post_tag = input("Enter tag of the forum's post body: ")
    thread_post_parameter = {}
    for i in range(int(input(f'How many parameters in a {thread_post_tag} tag? '))):
        if input("Do you need regular expressions for this tag? ") == 'Y':
            thread_post_parameter[input(f'Enter parameter {i+1} name: ')] = re.compile(input(f'Enter parameter {i+1} value: '))
        else:
            thread_post_parameter[input(f'Enter parameter {i+1} name: ')] = input(f'Enter parameter {i+1} value: ')
    forum_threads_tag = input("Enter tag of the thread's body on forum: ")
    forum_threads_parameter = {}
    for i in range(int(input(f'How many parameters in a {forum_threads_tag} tag? '))):
        if input("Do you need regular expressions for this tag? ") == 'Y':
            forum_threads_parameter[input(f'Enter parameter {i+1} name: ')] = re.compile(input(f'Enter parameter {i+1} value: '))
        else:
            forum_threads_parameter[input(f'Enter parameter {i+1} name: ')] = input(f'Enter parameter {i+1} value: ')

conn = sqlite3.connect('parser.db')
print('Succesfuly opend DB!')
# Name of file to save results to
FIRST_RESULTS = 'txt\\account_names.txt'
# Pulling banned words from the database
BANNED_EXCEPTIONS = []
cursor = conn.execute("SELECT word FROM banned_words")
for row in cursor:
    BANNED_EXCEPTIONS.append(row[0])
print('Fetched banned words!')
# Pulling key words from the database
KEY_WORDS = []
cursor = conn.execute("SELECT word FROM key_words")
for row in cursor:
    KEY_WORDS.append(row[0])
print('Fetched key words!')
conn.close()

TO_PARSE = []
for line in open('txt\\to_parse.txt', 'r'):
    TO_PARSE.append(str(line.rstrip()))

FORUM = input('Enter main link to the forum: ')
# Запускаем драйвер селениум
options_ = Options()
options_.page_load_strategy = 'eager'
s = Service("C:\\Program Files\\Mozilla Firefox\\geckodriver.exe")
driver = webdriver.Firefox(service=s, options=options_)

# Writes found telegram tags/names or other key words to the file
def find_names(forum_texts:list)->None:  
    with open(FIRST_RESULTS, 'a', encoding="utf-8") as file:
        for tag in forum_texts:
            for word in KEY_WORDS:
                if word in tag.text:
                    # Accepted characters: A-z (case-insensitive), 0-9 and underscores. Length: 5-32 characters.
                    nicknames =  re.findall(r".\B(?=\w{5,32}\b)[a-zA-Z0-9]+(?:_[a-zA-Z0-9]+)*", tag.text.split(word)[1])
                    for nick in nicknames:
                        if not (nick in BANNED_EXCEPTIONS):
                            file.write(nick + '\n')

# Scrapes text on thread's page
def scrape_page(forum_posts:ResultSet)->None:
    text = []
    for post in forum_posts:
        text.append(post.find(OtherSoft.message_tag, OtherSoft.message_parameter))
    find_names(text)

# Scrapes all pages in a thread
def scrape_thread(current_thread:str, s:requests.Session)->None:
    print(f'Scraping {current_thread}')

    html_text = str()
    if BOT_PROTECTION:
        driver.get(current_thread)
        html_text = driver.page_source
    else:
        html_text = s.get(current_thread).text
    
    soup = BeautifulSoup(html_text, 'html.parser')
    # Checking for pagination
    check_pagination = soup.find(OtherSoft.pagination_tag, OtherSoft.pagination_parameter)
    # Finding all posts for case where there are only one page in thread
    forum_posts = soup.find_all(OtherSoft.thread_post_tag, OtherSoft.thread_post_parameter)
    if check_pagination:
        scrape_page(forum_posts)
        check_same_ = Tag|NavigableString|None
        if PAGINATION_CASE == 'I':
            for i in range(2,5000):
                html_text = str()
                if BOT_PROTECTION:
                    driver.get(current_thread+PAGINATAION_TEMPLATE.format(i))
                    html_text = driver.page_source
                else:
                    html_text = s.get(current_thread+PAGINATAION_TEMPLATE.format(i)).text
                thread_soup = BeautifulSoup(html_text, "html.parser")
                check_same = thread_soup.find(OtherSoft.thread_post_tag, OtherSoft.thread_post_parameter)
                if check_same_ == check_same:
                    break
                else:
                    check_same_ = check_same 
                    forum_posts = thread_soup.find_all(OtherSoft.thread_post_tag, OtherSoft.thread_post_parameter)
                    scrape_page(forum_posts)
        if PAGINATION_CASE == 'C':
            for i in range(THREAD_STEP, 50000, THREAD_STEP):
                html_text = str()
                if BOT_PROTECTION:
                    driver.get(current_thread+PAGINATAION_TEMPLATE.format(i))
                    html_text = driver.page_source
                else:
                    html_text = s.get(current_thread+PAGINATAION_TEMPLATE.format(i)).text
                thread_soup = BeautifulSoup(html_text, "html.parser")
                check_same = thread_soup.find(OtherSoft.thread_post_tag, OtherSoft.thread_post_parameter)
                if check_same_ == check_same:
                    break
                else:
                    check_same_ = check_same 
                    forum_posts = thread_soup.find_all(OtherSoft.thread_post_tag, OtherSoft.thread_post_parameter)
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
    thread_links = forum_page.find_all(OtherSoft.forum_threads_tag, OtherSoft.forum_threads_parameter)
    for tag in thread_links:
        a_tags = tag.findChildren('a')
        if THREAD_LINK_POS:
            if ('https://' in a_tags[0]["href"]) or ('http://' in a_tags[0]["href"]):
                if len(a_tags) == 1:
                    scrape_thread(f'{a_tags[0]["href"]}', s)
                if len(a_tags) == THREAD_LINK_POS:
                    scrape_thread(f'{a_tags[THREAD_LINK_POS-1]["href"]}', s)
            else:
                if len(a_tags) == 1:
                    scrape_thread(f'{FORUM}{a_tags[0]["href"]}', s)
                if len(a_tags) == THREAD_LINK_POS:
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
        driver.get(forum_url)
        html_form = driver.page_source
    else:
        html_form = s.get(forum_url).text
    with open('check.html', 'w', encoding='utf-8') as file:
        file.write(html_form)
    soup = BeautifulSoup(html_form, "html.parser")
    # Checking for pagination of forum
    check_pagination = soup.find(OtherSoft.pagination_tag, OtherSoft.pagination_parameter)
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
                    driver.get(forum_url+PAGINATAION_TEMPLATE.format(i))
                    forum_page = BeautifulSoup(driver.page_source, "html.parser")
                else:
                    forum_page = BeautifulSoup(s.get(forum_url+PAGINATAION_TEMPLATE.format(i)).text, "html.parser")
                # Checking if we are on the last page
                check_same = forum_page.find(OtherSoft.forum_threads_tag, OtherSoft.forum_threads_parameter)
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
                    driver.get(forum_url+PAGINATAION_TEMPLATE.format(i))
                    forum_page = BeautifulSoup(driver.page_source, "html.parser")
                else:
                    forum_page = BeautifulSoup(s.get(forum_url+PAGINATAION_TEMPLATE.format(i)).text, "html.parser")
                # Checking if we are on the last page
                check_same = forum_page.find('title')
                if check_same_ == check_same:
                    break
                else:
                    # We are not on the last page, remembering unique info about current page...
                    check_same_ = check_same
                    # ...and scraping it
                    scrape_forum_page(s, forum_page)
                    print(f'{"-"*10}Scraped page {i}{"-"*10}\n')
                    page += 1
    else:
        scrape_forum_page(s, soup)
    print(f'\n\nScraped {forum_url}!\a')

def scrape_setup(s:requests.Session)->bool:
    global FORUM_STEP, THREAD_STEP, S_WORD_FLAG, THREAD_LINK_POS
    global PAGINATION_CASE, PAGINATAION_TEMPLATE, BOT_PROTECTION

    # Getting special str() in case it's needed to succesfully load links
    special_word = str()
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
        driver.close()

    # Starting to scrape forum using links provided in "txt/to_parse.txt"
    forum_url = str()
    for link in TO_PARSE:
        if S_WORD_FLAG:
            forum_url = FORUM + special_word + link
        else:
            forum_url = FORUM + link
        scrape_forum(s, forum_url)
    try:
        driver.close()
    except Exception as err:
        print(err)
        pass
    return True
        

def copy_cookies(s:requests.Session):
    for cookie in driver.get_cookies():
            c = {cookie['name']: cookie['value']}
            s.cookies.update(c)
    print("Cookies coppied successfully!")

def parse()->None:
    # Получаю куки-файлы из селениума и передаю их скрипту для
    # удачных реквестов страниц 
    driver.get(f"{FORUM}")
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
            A = False
    
    
parse()