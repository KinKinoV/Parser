from bs4 import BeautifulSoup, NavigableString, ResultSet, Tag
from time import sleep
from selenium import webdriver
import django
django.setup()
from django.shortcuts import render
from django.http import HttpResponse
from .models import Forum, Nickname, BannedFilter, KeyWordFilter
import gc, re, requests, json

class ParseSettings:
    message_tag = str
    message_parameter = {}
    pagination_tag = str
    pagination_parameter = {}
    thread_post_tag = str
    thread_post_parameter = {}
    thread_link_tag = str
    thread_link_parameter = {}
    forum_step = int
    thread_step = int
    pagination_case = str
    pagination_template = str
    bot_protection = False
    page_load_delay = float
    search_string = str
    forum_link = str
    login_requirment = False
    forumObject = Forum


    def __init__(self, link: str):
        try:
            parseConfs = Forum.objects.get(link=link).parseConfigs
        except Forum.DoesNotExist:
            print(f'There is no forum in the database with link "{link}".\n')
            exit()
        try:
            data = json.loads(parseConfs)
        except json.decoder.JSONDecodeError:
            print(f"\n{'='*30}\nError in file {__name__}.py!!!\n{'='*30}\nSomething wrong with the saved parseConfigs for thr {link}.\n\n")
            exit()
        regex_pattern = '/~/'
        
        self.forumObject = Forum.objects.get(link=link)
        self.message_tag = data['message_tag']
        for key, value in data['message_parameter'].items():
            if regex_pattern in value:
                self.message_parameter[key] = re.compile(value.strip(regex_pattern))
            else:
                self.message_parameter[key] = value

        self.pagination_tag = data['pagination_tag']
        for key, value in data['pagination_parameter'].items():
            if regex_pattern in value:
                self.pagination_parameter[key] = re.compile(value.strip(regex_pattern))
            else:
                self.pagination_parameter[key] = value

        self.thread_post_tag = data['thread_post_tag']
        for key, value in data['thread_post_parameter'].items():
            if regex_pattern in value:
                self.thread_post_parameter[key] = re.compile(value.strip(regex_pattern))
            else:
                self.thread_post_parameter[key] = value
        
        self.thread_link_tag = data['thread_link_tag']
        for key, value in data['thread_link_parameter'].items():
            if regex_pattern in value:
                self.thread_link_parameter[key] = re.compile(value.strip(regex_pattern))
            else:
                self.thread_link_parameter[key] = value

        self.pagination_case = data['pagination_case']
        
        if self.pagination_case == 'C':
            self.forum_step = int(data['forum_step'])
            self.thread_step = int(data['thread_step'])
        
        self.pagination_template = data['pagination_template']
        
        if data['bot_protection'] == 'True':
            self.bot_protection = True
        
        self.page_load_delay = float(data['page_load_delay'])
        # Temporary, later will be loaded from database too
        # For now this string can detect any possible telegram nickname
        self.search_string = '.\\B(?=\\w{5,32}\\b)[a-zA-Z0-9]+(?:_[a-zA-Z0-9]+)*'
        self.forum_link = link

        if data['login_requirment'] == 'True':
            self.login_requirment = True

def parse(*args)->None:
    global DRIVER, FORUM_SETTINGS, LOGIN_REQ, SITE_MESSAGES, PARSER_WORK
    FORUM_SETTINGS = ParseSettings(args[0])
    scrape_setup(args[1], args[2])

    options_ = webdriver.FirefoxOptions()
    options_.page_load_strategy = 'eager'
    DRIVER = webdriver.Remote("http://localhost:4444", options=options_)

    # Получаю куки-файлы из селениума и передаю их скрипту для
    # удачных реквестов страниц 
    DRIVER.get(f"{FORUM_SETTINGS.forum_link}")
    s = requests.Session()

    if FORUM_SETTINGS.login_requirment:
        while True:
            if LOGIN_REQ:
                copy_cookies(s)
                break
    else:
        copy_cookies(s)
    LOGIN_REQ = False

    if not FORUM_SETTINGS.bot_protection:
        DRIVER.quit()
    
    start_parse(s)
    
    SITE_MESSAGES.append("Остановка скрипта...") # Добавить вывод на сайт
    PARSER_WORK = False
    try:
        DRIVER.quit()
    except Exception:
        pass
    SITE_MESSAGES.clear()

def copy_cookies(s:requests.Session):
    for cookie in DRIVER.get_cookies():
            c = {cookie['name']: cookie['value']}
            s.cookies.update(c)
    SITE_MESSAGES.append("Куки-файлы успешно скопированы!")

def scrape_setup(toParse:str, resultFilter:str)->bool:

    global BANNED_EXCEPTIONS, KEY_WORDS, TO_PARSE

    BANNED_EXCEPTIONS = BannedFilter.objects.get(purpose=resultFilter).filter.splitlines()
    
    KEY_WORDS = KeyWordFilter.objects.get(purpose=resultFilter).filter.splitlines()

    TO_PARSE = toParse.splitlines()

def start_parse(s:requests.Session)-> bool:
    global PARSER_WORK
    PARSER_WORK = True
    forum_url = str()
    for link in TO_PARSE:
        forum_url = FORUM_SETTINGS.forum_link + link
        scrape_forum(s, forum_url)

def kill_parse():
    global DRIVER, LOGIN_REQ

    LOGIN_REQ = False
    DRIVER.quit()

# Scraping all threads of the current forum
def scrape_forum(s:requests.Session, forum_url:str):
    SITE_MESSAGES.append(f'\n\nПроизовдится поиск по теме {forum_url}...\n')
    html_form = str()
    if FORUM_SETTINGS.bot_protection:
        DRIVER.get(forum_url)
        sleep(FORUM_SETTINGS.page_load_delay)
        html_form = DRIVER.page_source
    else:
        html_form = s.get(forum_url).text
        sleep(FORUM_SETTINGS.page_load_delay)
    soup = BeautifulSoup(html_form, "html.parser")
    # Checking for pagination of forum
    check_pagination = soup.find(FORUM_SETTINGS.pagination_tag, FORUM_SETTINGS.pagination_parameter)
    if check_pagination:
        scrape_forum_page(s, soup)
        SITE_MESSAGES.append(f'{"-"*10}Страница 1 завершена{"-"*10}\n')
        del(soup)
        gc.collect()
        check_same_link = Tag|NavigableString|None
        check_same_title = Tag|NavigableString|None
        if FORUM_SETTINGS.pagination_case == 'I':
            for i in range(2, 5000):
                # Creating soup of the current page
                forum_page = None
                if FORUM_SETTINGS.bot_protection:
                    DRIVER.get(forum_url+FORUM_SETTINGS.pagination_template.format(i))
                    sleep(FORUM_SETTINGS.page_load_delay)
                    forum_page = BeautifulSoup(DRIVER.page_source, "html.parser")
                else:
                    forum_page = BeautifulSoup(s.get(forum_url+FORUM_SETTINGS.pagination_template.format(i)).text, "html.parser")
                    sleep(FORUM_SETTINGS.page_load_delay)
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
                    SITE_MESSAGES.append(f'{"-"*10}Страница {i} завершена{"-"*10}\n')
        if FORUM_SETTINGS.pagination_case == 'C':
            page = 2
            for i in range(FORUM_SETTINGS.forum_step, 50000, FORUM_SETTINGS.forum_step):    
                # Creating soup of the current page
                forum_page = None
                if FORUM_SETTINGS.bot_protection:
                    DRIVER.get(forum_url+FORUM_SETTINGS.pagination_template.format(i))
                    sleep(FORUM_SETTINGS.page_load_delay)
                    forum_page = BeautifulSoup(DRIVER.page_source, "html.parser")
                else:
                    forum_page = BeautifulSoup(s.get(forum_url+FORUM_SETTINGS.pagination_template.format(i)).text, "html.parser")
                    sleep(FORUM_SETTINGS.page_load_delay)
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
                    SITE_MESSAGES.append(f'{"-"*10}Страница {page} завершена{"-"*10}\n')
                    page += 1
    else:
        scrape_forum_page(s, soup)
    
    SITE_MESSAGES.append(f'\n\nПоиск по теме {forum_url} завершен!\a')    

# Scraping BS of current forum page
def scrape_forum_page(s:requests.Session, forum_page:BeautifulSoup):
    thread_links = forum_page.find_all(FORUM_SETTINGS.thread_link_tag, FORUM_SETTINGS.thread_link_parameter)
    for tag in thread_links:
        a_tags = tag.findChildren('a')
        pos_ = 0
        while True:
            if len(a_tags) == 1:
                if ('https://' in a_tags[0]["href"]) or ('http://' in a_tags[0]["href"]):
                    scrape_thread(f'{a_tags[0]["href"]}', s)
                    break
                else:
                    scrape_thread(f'{FORUM_SETTINGS.forum_link}{a_tags[0]["href"]}', s)
                    break
            else:
                if not('prefix_id' in a_tags[pos_]["href"]):
                    if ('https://' in a_tags[pos_]["href"]) or ('http://' in a_tags[pos_]["href"]):
                        scrape_thread(f'{a_tags[pos_]["href"]}', s)
                        break
                    else:
                        scrape_thread(f'{FORUM_SETTINGS.forum_link}{a_tags[pos_]["href"]}', s)
                        break
                else:
                    pos_ = pos_ + 1

# Scrapes all pages in a thread
def scrape_thread(current_thread:str, s:requests.Session)->None:
    SITE_MESSAGES.append(f'Поиск в {current_thread}')

    html_text = str()
    if FORUM_SETTINGS.bot_protection:
        DRIVER.get(current_thread)
        sleep(FORUM_SETTINGS.page_load_delay)
        html_text = DRIVER.page_source
    else:
        html_text = s.get(current_thread).text
        sleep(FORUM_SETTINGS.page_load_delay)
    
    soup = BeautifulSoup(html_text, 'html.parser')
    # Checking for pagination
    check_pagination = soup.find(FORUM_SETTINGS.pagination_tag, FORUM_SETTINGS.pagination_parameter)
    # Finding all posts for case where there are only one page in thread
    forum_posts = soup.find_all(FORUM_SETTINGS.thread_post_tag, FORUM_SETTINGS.thread_post_parameter)
    if check_pagination:
        scrape_page(forum_posts)
        check_same_link = Tag|NavigableString|None
        check_same_title = Tag|NavigableString|None
        if FORUM_SETTINGS.pagination_case == 'I':
            for i in range(2,5000):
                html_text = str()
                if FORUM_SETTINGS.bot_protection:
                    DRIVER.get(current_thread+FORUM_SETTINGS.pagination_template.format(i))
                    sleep(FORUM_SETTINGS.page_load_delay)
                    html_text = DRIVER.page_source
                else:
                    html_text = s.get(current_thread+FORUM_SETTINGS.pagination_template.format(i)).text
                    sleep(FORUM_SETTINGS.page_load_delay)
                thread_soup = BeautifulSoup(html_text, "html.parser")
                check_same_1 = thread_soup.find('link', {'rel' : 'canonical'})
                check_same_2 = thread_soup.find('title')
                if (check_same_link == check_same_1) and (check_same_title == check_same_2):
                    break
                else:
                    check_same_link = check_same_1
                    check_same_title = check_same_2
                    forum_posts = thread_soup.find_all(FORUM_SETTINGS.thread_post_tag, FORUM_SETTINGS.thread_post_parameter)
                    scrape_page(forum_posts)
        if FORUM_SETTINGS.pagination_case == 'C':
            for i in range(FORUM_SETTINGS.thread_step, 50000, FORUM_SETTINGS.thread_step):
                html_text = str()
                if FORUM_SETTINGS.bot_protection:
                    DRIVER.get(current_thread+FORUM_SETTINGS.pagination_template.format(i))
                    sleep(FORUM_SETTINGS.page_load_delay)
                    html_text = DRIVER.page_source
                else:
                    html_text = s.get(current_thread+FORUM_SETTINGS.pagination_template.format(i)).text
                    sleep(FORUM_SETTINGS.page_load_delay)
                thread_soup = BeautifulSoup(html_text, "html.parser")
                check_same_1 = thread_soup.find('link', {'rel' : 'canonical'})
                check_same_2 = thread_soup.find('title')
                if (check_same_link == check_same_1) and (check_same_title == check_same_2) :
                    break
                else:
                    check_same_link = check_same_1
                    check_same_title = check_same_2 
                    forum_posts = thread_soup.find_all(FORUM_SETTINGS.thread_post_tag, FORUM_SETTINGS.thread_post_parameter)
                    scrape_page(forum_posts)
    else:
        scrape_page(forum_posts)
    SITE_MESSAGES.append("Успешно проверили!\n")
    del(soup)
    del(check_pagination)
    del(forum_posts)
    gc.collect()

# Scrapes text on thread's page
def scrape_page(forum_posts:ResultSet)->None:
    text = []
    for post in forum_posts:
        text.append(post.find(FORUM_SETTINGS.message_tag, FORUM_SETTINGS.message_parameter))
    find_names(text)

# Writes found telegram tags/names or other key words to the file
def find_names(forum_texts:list)->None:
    total_found = 0  
    for tag in forum_texts:
        for word in KEY_WORDS:
            if word in tag.text:
                # While writing regex pattern in python !USE! '\\' for one '\'
                found_data =  re.findall(FORUM_SETTINGS.search_string, tag.text.split(word)[1])
                for data in found_data:
                    total_found += 1
                    if not (data in BANNED_EXCEPTIONS) and not Nickname.objects.filter(handler=data).exists():
                        Nickname(handler=data, forumOrigin=FORUM_SETTINGS.forumObject).save()
    SITE_MESSAGES.append(f'Найдено {total_found} совпадений.')


# PARSER SETTINGS FOR PARSE

# Tags to use in scraping
FORUM_SETTINGS = None
# Selenium driver to use
DRIVER = None

LOGIN_REQ = False
PARSER_WORK = False

def loginReqCheck(request):
    global LOGIN_REQ
    if request.method == 'POST' and request.POST.get('loginCheck') == "True":
        LOGIN_REQ = True
        return render(request, 'parser/partials/stopButton.html')
    return HttpResponse('OK')

# Fetched from the DB
# Words to NOT to write to result file
BANNED_EXCEPTIONS = []
# If any in thread's message, start searching for needed data
KEY_WORDS = []

TO_PARSE=[]

SITE_MESSAGES = []