from bs4 import BeautifulSoup, NavigableString, ResultSet, Tag
from enum import Enum
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
import os
import gc
import keyboard
import re
import requests
import sqlite3

SITE_TAGS = None
FORUM_STEP = int()
THREAD_STEP = int()

def start():
    forum_soft = input("Enter software name on which forum is working\nPossible variants:\n\t1.Xceref\n\t2.phpBB\n\t3.Other\nEnter name or number:")

    if forum_soft == 'Xceref' or forum_soft == '1':
        os.system('py Xceref.py')
        exit()
    elif forum_soft == 'phpBB' or forum_soft == '2':
        os.system('py phpBB.py')
        exit()
    elif forum_soft == 'Other' or forum_soft == '3':
        class OtherSoft(Enum):
            message_tag = input("Enter tag where post's text is: ")
            message_class = input("Enter class where post's text is: ")
            pagination_tag = input("Enter tag of the pagination module: ")
            pagination_class = input("Enter class of the pagination module: ")
            thread_post_tag = input("Enter tag of the forum's post body: ")
            thread_post_class = input("Enter class of the forum's post body: ")
            forum_threads_tag = input("Enter tag of the thread's body on forum: ")
            forum_threads_class = input("enter class of the thread's body on forum: ")
        SITE_TAGS = OtherSoft
    else:
        print("You didn't enter right parameter, please enter one of the avaible variants.")

if __name__ == '__main__':
    start()

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
s = Service("C:\\Program Files\\Mozilla Firefox\\geckodriver.exe")
driver = webdriver.Firefox(service=s)

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
        text.append(post.find(SITE_TAGS.message_tag.value, { 'class' : SITE_TAGS.message_class.value}))
    find_names(text)

# Scrapes all pages in a thread
def scrape_thread(current_thread:str, s:requests.Session)->None:
    print(f'Scraping {current_thread}')
    soup = BeautifulSoup(s.get(current_thread).text, 'html.parser')
    # Checking for pagination
    check_pagination = soup.find(SITE_TAGS.pagination_tag.value, class_=SITE_TAGS.pagination_class.value)
    # Finding all posts for case where there are only one page in thread
    forum_posts = soup.find_all(SITE_TAGS.thread_post_tag.value, class_=SITE_TAGS.thread_post_class.value)
    if check_pagination:
        scrape_page(forum_posts)
        check_same_ = Tag|NavigableString|None
        for i in range(2,500):
            thread_soup = BeautifulSoup(s.get(current_thread+f'page-{i}').text, "html.parser")
            check_same = thread_soup.find(SITE_TAGS.thread_post_tag.value, class_=SITE_TAGS.thread_post_class.value)
            if check_same_ == check_same:
                break
            else:
                check_same_ = check_same 
                forum_posts = thread_soup.find_all(SITE_TAGS.thread_post_tag.value, class_=SITE_TAGS.thread_post_class.value)
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
    thread_links = forum_page.find_all(SITE_TAGS.forum_threads_tag.value, class_=SITE_TAGS.forum_threads_class.value)
    for tag in thread_links:
        a_tags = tag.findChildren('a')
        if len(a_tags) == 1:
            scrape_thread(f'{FORUM}{a_tags[0]["href"]}', s)
        if len(a_tags) == 2:
            scrape_thread(f'{FORUM}{a_tags[1]["href"]}', s)         

# Scraping all threads of the current forum
def scrape_forum(s:requests.Session, forum_url:str, pagination_case:str, pagination_template:str):
    print(f'\n\nScrapping {forum_url}...\n')
    html_form = s.get(forum_url).text
    soup = BeautifulSoup(html_form, "html.parser")
    # Checking for pagination of forum
    check_pagination = soup.find(SITE_TAGS.pagination_tag.value, class_=SITE_TAGS.pagination_class.value)
    if check_pagination:
        scrape_forum_page(s, soup)
        print(f'{"-"*10}Scraped page 1 {"-"*10}\n')
        del(soup)
        gc.collect()
        check_same_ = Tag|NavigableString|None
        if pagination_case == 'I':
            for i in range(2, 500):
                # Creating soup of the current page
                forum_page = BeautifulSoup(s.get(forum_url+pagination_template.format(i)).text, "html.parser")
                # Checking if we are on the last page
                check_same = forum_page.find(SITE_TAGS.forum_threads_tag.value, class_=SITE_TAGS.forum_threads_class.value)
                if check_same_ == check_same:
                    break
                else:
                    # We are not on the last page, remembering unique info about current page...
                    check_same_ = check_same
                    # ...and scraping it
                    scrape_forum_page(s, forum_page)
                    print(f'{"-"*10}Scraped page {i}{"-"*10}\n')
        if pagination_case == 'C':
            page = 2
            for i in range(FORUM_STEP, 50000, FORUM_STEP):    
                # Creating soup of the current page
                forum_page = BeautifulSoup(s.get(forum_url+pagination_template.format(i)).text, "html.parser")
                # Checking if we are on the last page
                check_same = forum_page.find(SITE_TAGS.forum_threads_tag.value, class_ = SITE_TAGS.forum_threads_class.value)
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
    global FORUM_STEP, THREAD_STEP
    special_word = str()
    s_word_flag = True
    if input('Do you need to add special words to base forum link before links to the themed pages? [Y] -- Yes, [N] -- No\n') == 'Y':
        special_word = input('Then enter this word: ')
    else:
        s_word_flag = False
        del(special_word)
        gc.collect()
    pagination_case = input('How pagination works on this forum? Just by incrementing value (adding 1,2,3,...,100 to something like "page" or "index") \
            or by counting post/threads (something like: ...&?start=15/30/45)?\n [I] -- Incrementing, [C] -- counting')
    if pagination_case == 'C':
        print("You've chosen [C], please enter next data:")
        FORUM_STEP = int(input('Enter step for pagination for pages with threads(in phpBB usually 50): '))
        THREAD_STEP = int(input('Enter step for pagination for threads with posts(in phpBB usually 15): '))
    pagination_template =  input("Please, enter template that is added to the end of url with {{}} where page number is placed: ")
    forum_url = str()
    for link in TO_PARSE:
        if s_word_flag:
            forum_url = FORUM + special_word + link
        else:
            forum_url = FORUM + link
        scrape_forum(s, forum_url, pagination_case, pagination_template)
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
    driver.close()
    
    # Цикл для ручного запуска парсинга форума или остановки скрипта
    A = True
    while A:
        if keyboard.is_pressed("S"):
            A = scrape_setup(s)
        if keyboard.is_pressed("Q"):
            print("Stopping script!")
            A = False
    
    
parse()