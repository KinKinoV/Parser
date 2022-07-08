from bs4 import BeautifulSoup, NavigableString, ResultSet, Tag
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from parseconfigs import phpBB
import gc
import re
import keyboard
import requests
import sqlite3

BANNED_EXCEPTIONS = []
KEY_WORDS = []
TO_PARSE = []
# Name of file to save results to
FIRST_RESULTS = 'txt\\account_names.txt'

conn = sqlite3.connect('parser.db')
print('Succesfuly opend DB!')

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

#Getting forum themes links to parse through
for line in open('txt\\to_parse.txt', 'r'):
    TO_PARSE.append(str(line.rstrip()))

site_tags = phpBB
PAGE_STEP = int(input("Enter forum's ammount of messages on ONE page of a thread (usually 15): "))
FORUM_STEP = int(input("Enter forum's ammount of threads on ONE page (usually 50): "))
POST_BODY_TITLE = input("Enter post's body 'title' name: ")

FORUM = input('Enter main link to the forum: ')
s = Service("C:\\Program Files\\Mozilla Firefox\\geckodriver.exe")
driver = webdriver.Firefox(service=s)

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
def scrape_page_phpBB(forum_posts:ResultSet)->None:
    text = []
    for post in forum_posts:
        text.append(post.find(site_tags.message_tag.value, { 'class' : site_tags.message_class.value}))
    find_names(text)

# Scrapes all pages in a thread
def scrape_thread_phpBB(current_thread:str, s:requests.Session)->None:
    print(f'Scraping {current_thread}')
    soup = BeautifulSoup(s.get(current_thread).text, 'html.parser')
    # Checking for pagination
    check_pagination = soup.find(site_tags.pagination_tag.value, class_=site_tags.pagination_class.value)
    # Finding all posts for case where there are only one page in thread
    forum_posts = soup.find_all(site_tags.thread_post_tag.value, class_=site_tags.thread_post_class.value)
    if check_pagination:
        scrape_page_phpBB(forum_posts)
        check_same_ = Tag|NavigableString|None
        for i in range(PAGE_STEP, 5000, PAGE_STEP):
            thread_soup = BeautifulSoup(s.get(current_thread+f'&start={i}').text, "html.parser")
            check_same = thread_soup.find('div', class_='postbody')
            if check_same_ == check_same:
                break
            else:
                check_same_ = check_same 
                forum_posts = thread_soup.find_all('div', class_='postbody')
                scrape_page_phpBB(forum_posts)
    else:
        scrape_page_phpBB(forum_posts)
    print("Succesfully scraped!\n")
    del(soup)
    del(check_pagination)
    del(forum_posts)
    gc.collect()

# Scraping BS of current forum page
def scrape_forum_page_phpBB(s:requests.Session, forum_page:BeautifulSoup):
    #, class_=SiteTags.forum_threads_class.value  Нет новых сообщений No unread posts
    thread_links = forum_page.find_all('dt', title=POST_BODY_TITLE)
    for tag in thread_links:
        a_tags = tag.findChildren('a')
        scrape_thread_phpBB(f'{FORUM}{a_tags[0]["href"]}', s)


# Scraping all threads of the current forum
def scrape_forum_phpBB(s:requests.Session)->bool:
    for link in TO_PARSE:
        forum_url = FORUM + link
        html_form = s.get(forum_url).text
        soup = BeautifulSoup(html_form, "html.parser")
        # Checking for pagination of forum
        check_pagination = soup.find(site_tags.pagination_tag.value, class_=site_tags.pagination_class.value)
        if check_pagination:
            scrape_forum_page_phpBB(s, soup)
            print(f'{"-"*10}Scraped 50 threads{"-"*10}\n')
            del(soup)
            gc.collect()
            check_same_ = Tag|NavigableString|None
            for i in range(FORUM_STEP, 5000, FORUM_STEP):
                # Creating soup of the current page
                forum_page = BeautifulSoup(s.get(forum_url+f'&start={i}').text, "html.parser")
                # Checking if we are on the last page , class_=SiteTags.forum_threads_class.value
                check_same = forum_page.find('dt', title=POST_BODY_TITLE)
                if check_same_ == check_same:
                    break
                else:
                    # We are not on the last page, remembering unique info about current page...
                    check_same_ = check_same
                    # ...and scraping it
                    scrape_forum_page_phpBB(s, forum_page)
                    print(f'{"-"*10}Scraped {i} threads{"-"*10}\n')
        else:
            # If no pagination, scraping current soup and outputting html page in case of error
            with open('site_save.html', 'w') as file:
                file.write(html_form)
            scrape_forum_page_phpBB(s, soup)
        print(f'\n\nScraped {forum_url}!\a')
    return True

def parsePhpBB()->None:
    # Получаю куки-файлы из селениума и передаю их скрипту для
    # удачных реквестов страниц 
    driver.get(FORUM)

    s = requests.Session()
    for cookie in driver.get_cookies():
        c = {cookie['name']: cookie['value']}
        s.cookies.update(c)
    print("Cookies coppied successfully!")

    # Цикл для ручного запуска парсинга форума или остановки скрипта
    A = True
    while A:
        if keyboard.is_pressed("S"):
            A = scrape_forum_phpBB(s)
        if keyboard.is_pressed("Q"):
            print("Stopping script!")
            A = False
    driver.close()

parsePhpBB()