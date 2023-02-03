from bs4 import BeautifulSoup, NavigableString, ResultSet, Tag
from time import sleep
import undetected_chromedriver as uc
from selenium import webdriver
# from selenium.webdriver.firefox.service import Service
# from selenium.webdriver.firefox.options import Options
import gc
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
# Selenium driver to use
DRIVER = None

SEARCH_STRING = str()

# Fetched from the DB
# Words to NOT to write to result file
BANNED_EXCEPTIONS = []
# If any in thread's message, start searching for needed data
KEY_WORDS = []

TO_PARSE=[]

DEBUG_MODE = False

# Writes found telegram tags/names or other key words to the file
def find_names(forum_texts:list)->None:
    total_found = 0  
    with open(FIRST_RESULTS, 'a', encoding="utf-8") as file:
        for tag in forum_texts:
            for word in KEY_WORDS:
                if word in tag.text:
                    # While writing regex pattern in python !USE! '\\' for one '\'
                    found_data =  re.findall(SEARCH_STRING, tag.text.split(word)[1])
                    for data in found_data:
                        total_found += 1
                        if not (data in BANNED_EXCEPTIONS):
                            file.write(data + '\n')
    print(f'Найдено {total_found} совпадений.')

# Scrapes text on thread's page
def scrape_page(forum_posts:ResultSet)->None:
    text = []
    for post in forum_posts:
        text.append(post.find(SITE_TAGS.message_tag, SITE_TAGS.message_parameter))
    find_names(text)

# Scrapes all pages in a thread
def scrape_thread(current_thread:str, s:requests.Session)->None:
    print(f'Поиск в {current_thread}')

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
        check_same_link = Tag|NavigableString|None
        check_same_title = Tag|NavigableString|None
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
                check_same_1 = thread_soup.find('link', {'rel' : 'canonical'})
                check_same_2 = thread_soup.find('title')
                if (check_same_link == check_same_1) and (check_same_title == check_same_2):
                    break
                else:
                    check_same_link = check_same_1
                    check_same_title = check_same_2
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
                check_same_1 = thread_soup.find('link', {'rel' : 'canonical'})
                check_same_2 = thread_soup.find('title')
                if (check_same_link == check_same_1) and (check_same_title == check_same_2) :
                    break
                else:
                    check_same_link = check_same_1
                    check_same_title = check_same_2 
                    forum_posts = thread_soup.find_all(SITE_TAGS.thread_post_tag, SITE_TAGS.thread_post_parameter)
                    scrape_page(forum_posts)
    else:
        scrape_page(forum_posts)
    print("Успешно проверили!\n")
    del(soup)
    del(check_pagination)
    del(forum_posts)
    gc.collect()

# Scraping BS of current forum page
def scrape_forum_page(s:requests.Session, forum_page:BeautifulSoup):
    thread_links = forum_page.find_all(SITE_TAGS.forum_threads_tag, SITE_TAGS.forum_threads_parameter)
    for tag in thread_links:
        a_tags = tag.findChildren('a')
        pos_ = 0
        while True:
            if len(a_tags) == 1:
                if ('https://' in a_tags[0]["href"]) or ('http://' in a_tags[0]["href"]):
                    scrape_thread(f'{a_tags[0]["href"]}', s)
                    break
                else:
                    scrape_thread(f'{FORUM}{a_tags[0]["href"]}', s)
                    break
            else:
                if not('prefix_id' in a_tags[pos_]["href"]):
                    if ('https://' in a_tags[pos_]["href"]) or ('http://' in a_tags[pos_]["href"]):
                        scrape_thread(f'{a_tags[pos_]["href"]}', s)
                        break
                    else:
                        scrape_thread(f'{FORUM}{a_tags[pos_]["href"]}', s)
                        break
                else:
                    pos_ = pos_ + 1

# Scraping all threads of the current forum
def scrape_forum(s:requests.Session, forum_url:str):
    print(f'\n\nПроизовдится поиск по теме {forum_url}...\n')
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
        print(f'{"-"*10}Страница 1 завершена{"-"*10}\n')
        del(soup)
        gc.collect()
        check_same_link = Tag|NavigableString|None
        check_same_title = Tag|NavigableString|None
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
                check_same_1 = forum_page.find('link', {'rel' : 'canonical'})
                check_same_2 = forum_page.find('title')
                
                if (check_same_link == check_same_1) and (check_same_title == check_same_2):
                    break
                else:
                    # We are not on the last page, remembering unique info about current page...
                    check_same_link = check_same_1
                    check_same_title = check_same_2
                    # ...and scraping it
                    scrape_forum_page(s, forum_page)
                    print(f'{"-"*10}Страница {i} завершена{"-"*10}\n')
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
                check_same_1 = forum_page.find('link', {'rel' : 'canonical'})
                check_same_2 = forum_page.find('title')
                if (check_same_link == check_same_1) and (check_same_title == check_same_2):
                    break
                else:
                    # We are not on the last page, remembering unique info about current page...
                    check_same_link = check_same_1
                    check_same_title = check_same_2
                    # ...and scraping it
                    scrape_forum_page(s, forum_page)
                    print(f'{"-"*10}Страница {page} завершена{"-"*10}\n')
                    page += 1
    else:
        scrape_forum_page(s, soup)
    
    print(f'\n\nПоиск по теме {forum_url} завершен!\a')    

def scrape_setup()->bool:

    global BANNED_EXCEPTIONS, KEY_WORDS, TO_PARSE, FORUM
    global FORUM_STEP, THREAD_STEP
    global PAGINATION_CASE, PAGINATAION_TEMPLATE, BOT_PROTECTION
    global PAGE_LOAD_DELAY, SEARCH_STRING

    PAGINATION_CASE = SITE_TAGS.pagination_case
    if PAGINATION_CASE == 'C':
        FORUM_STEP = SITE_TAGS.forum_step
        THREAD_STEP = SITE_TAGS.thread_step
    PAGINATAION_TEMPLATE = SITE_TAGS.pagination_template
    BOT_PROTECTION = SITE_TAGS.bot_protection
    PAGE_LOAD_DELAY = SITE_TAGS.page_load_delay
    SEARCH_STRING = SITE_TAGS.search_string
    FORUM = SITE_TAGS.forum_link

    conn = sqlite3.connect('migrations/parser.db')
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

    for line in open('data\\to_parse.txt', 'r'):
        TO_PARSE.append(str(line.rstrip()))
        
def start_parse(s:requests.Session)-> bool:
    
    forum_url = str()
    for link in TO_PARSE:
        forum_url = FORUM + link
        scrape_forum(s, forum_url)

def copy_cookies(s:requests.Session):
    for cookie in DRIVER.get_cookies():
            c = {cookie['name']: cookie['value']}
            s.cookies.update(c)
    print("Куки успешно скопированы!")

def parse()->None:
    global FORUM, DRIVER, SITE_TAGS
    scrape_setup()

    options_ = uc.ChromeOptions()
    options_.page_load_strategy = 'eager'
    DRIVER = uc.Chrome(options=options_)

    # Получаю куки-файлы из селениума и передаю их скрипту для
    # удачных реквестов страниц 
    DRIVER.get(f"{FORUM}")
    s = requests.Session()

    if SITE_TAGS.login_requirment:
        print('Пожалуйста, перейдите в новое окно, что открылось и войдите в аккаунт.\n')
        if input('Вы завершили вход? Если да, введите [Y] : ') == 'Y':
            copy_cookies(s)
        else:
            print("Вы ввели не 'Y'! Скрипт останавливается...")
            return
    else:
        copy_cookies(s)

    if not SITE_TAGS.bot_protection:
        DRIVER.quit()
    
    start_parse(s)

    print("Остановка скрипта...")
    
    try:
        DRIVER.quit()
    except Exception:
        pass
    

def start():
    global SITE_TAGS
    try:
        print('\n\nПожалуйста, перейдите по ссылке http://localhost:5000/ и введите все нужные данные.\n')
        os.system("py server.py")
    except KeyboardInterrupt:
        print('Сервер остановлен!')
        pass
    SITE_TAGS = parseconfigs.ParseSettings()
    
    parse()
    
if __name__ == '__main__':
    start()