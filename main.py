from bs4 import BeautifulSoup, NavigableString, ResultSet, Tag
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
import gc
import keyboard
import re
import requests

# Name of file to save results to
FIRST_RESULTS = 'txt\\account_names.txt'

# Temporary!!! Later will be pulled from the database
BANNED_EXCEPTIONS = ['Telegram', 'Jabber', 'Driver', 'Yandex', 'TELEGRAM', 'License', 'Republic', 'Passport', 'Driving',
                    'template', 'ENGLISH', 'VERSION', 'Service', 'YANDEX', 'Yandex', 'yandex', 'version', 'Version', 'english',
                    'English', 'Discount', 'contacts', 'communication', 'twitter', 'Twitter', 'TWITTER', 'google', 'Google',
                    'account', 'Account', 'ACCOUNT', 'tiktok', 'TIKTOK', 'TikTok', 'Tiktok', 'handed', 'various', 'communal', 'services', 'statements', 'telegram', 'WesternUnion', 'viewtopic', 'WebMoney', 'LiqPay', 'PerfectMoney', 'Payeer', 'TeleMoney', 'Bitcoin', 'youtube', 'subscribers', 'subscriptions', 'social', 'networks', 'yourself', 'dislikes', 'publics', 'popularity', 'popular', 'famous', 'buying', 'instagram', 'Vkontakte', 'classmates', 'cheating', 'publications', 'offers', 'public', 'friends', 'Welcome', 'application', 'messenger', 'github', 'webogram', 'random', 'Example', 'Database', 'Personal', 'number', 'documents', 'instructions', 'Barcodes', 'contents', 'licenses', 'bitcoin', 'IPhone', 'market', 'product', 'context', 'search', 'Adidas', 'Climawarm', 'adidas', 'pukhovik', 'climawarm', 'Reebok', 'Classic', 'reebok', 'krossovki', 'krosovki', 'Disney', 'Princess', 'Frozen', 'Marvel', 'marvel', 'Heroes', 'heroes', 'Smashbox', 'Giorgio', 'Armani', 'Loreal', 'Lancome', 'Huawei', 'huawei', 'Xiaomi', 'xiaomi', 'mi', 'Redmi', 'RealMe', 'telega', 'Revolut', 'LeoPay', 'Kraken', 'Bitzlato', 'Binance', 'Bittrex', 'Poloniex', 'Coinpayments', 'Okcoin', 'Bitlish', 'Liteforex', 'Epaycore', 'airbnb', 'Webmoney']

# Also temporary! Later will be pulled from the database or taken from the user
KEY_WORDS = ['@', 'ТГ ', ' тг', 'Телеграмм', 'телеграм', 'телега', ' пиши ', 'Пиши']


# Ловим и записываем ошибки (error_log.txt)
try:
    # Запускаем драйвер селениум
    s = Service("C:\\Program Files\\Mozilla Firefox\\geckodriver.exe")
    driver = webdriver.Firefox(service=s)
    forum_= input('Enter main link to the forum: ')
    #forum_ = "https://s2.piratebuhta.info"

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
            text.append(post.find('div', { 'class' : 'bbWrapper'}))    
        find_names(text)

    # Scrapes all pages in a thread
    def scrape_thread(current_thread:str, s:requests.Session)->None:
        print(f'Scraping {current_thread}')
        soup = BeautifulSoup(s.get(current_thread).text, 'html.parser')
        # Checking for pagination
        check_pagination = soup.find('ul', class_="pageNav-main")
        # Finding all posts for case where there are only one page in thread
        forum_posts = soup.find_all('article', class_="message-body js-selectToQuote")
        if check_pagination:
            scrape_page(forum_posts)
            check_same_ = Tag|NavigableString|None
            for i in range(2,500):
                thread_soup = BeautifulSoup(s.get(current_thread+f'page-{i}').text, "html.parser")
                check_same = thread_soup.find('article', class_="message-body js-selectToQuote")
                if check_same_ == check_same:
                    break
                else:
                    check_same_ = check_same 
                    forum_posts = thread_soup.find_all('article', class_="message-body js-selectToQuote")
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
        thread_links = forum_page.find_all('div', class_="structItem-title")
        for tag in thread_links:
            a_tags = tag.findChildren('a')
            if len(a_tags) == 1:
                scrape_thread(f'{forum_}{a_tags[0]["href"]}', s)
            if len(a_tags) == 2:
                scrape_thread(f'{forum_}{a_tags[1]["href"]}', s)         

    # Scraping all threads of the current forum
    def scrape_forum(s:requests.Session)->bool:
        forum_url = driver.current_url
        html_form = s.get(forum_url).text
        soup = BeautifulSoup(html_form, "html.parser")
        # Checking for pagination of forum
        check_pagination = soup.find('ul', class_="pageNav-main")
        if check_pagination:
            scrape_forum_page(s, soup)
            print(f'{"-"*10}Scraped page 1 {"-"*10}\n')
            del(soup)
            gc.collect()
            check_same_ = Tag|NavigableString|None
            for i in range(2, 500):
                # Creating soup of the current page
                forum_page = BeautifulSoup(s.get(forum_url+f'page-{i}').text, "html.parser")
                # Checking if we are on the last page
                check_same = forum_page.find('div', class_="structItem-title")
                if check_same_ == check_same:
                    break
                else:
                    # We are not on the last page, remembering unique info about current page...
                    check_same_ = check_same
                    # ...and scraping it
                    scrape_forum_page(s, forum_page)
                    print(f'{"-"*10}Scraped page {i}{"-"*10}\n')
        else:
            # If no pagination, scraping current soup and outputting html page in case of error
            with open('site_save.html', 'w') as file:
                file.write(html_form)
            scrape_forum_page(s, soup)
        print(f'\n\nScraped {forum_url}!\a')
        return True

    def parse()->None:
        # Получаю куки-файлы из селениума и передаю их скрипту для
        # удачных реквестов страниц 
        driver.get(f"{forum_}/login")
        driver.find_element(By.NAME, "login").send_keys("KinKin")
        driver.find_element(By.NAME, "password").send_keys("UResezure21!")

        s = requests.Session()
        if input('Have you completed login? Enter [Y] to continue: ') == 'Y':
            for cookie in driver.get_cookies():
                c = {cookie['name']: cookie['value']}
                s.cookies.update(c)
            print("Cookies coppied successfully!")
        else:
            print("You didn't enter Y!")
            return
        # Цикл для ручного запуска парсинга форума или остановки скрипта
        A = True
        while A:
            if keyboard.is_pressed("S"):
                A = scrape_forum(s)
            if keyboard.is_pressed("Q"):
                print("Stopping script!")
                A = False
        driver.close()
        
    if __name__ == '__main__':
        parse()

except Exception as e:
        print(e)
        with open('txt\\error_log.txt', 'a') as log:
            log.write(f'{datetime.now()}\n{e}\n\n')
        driver.close()
