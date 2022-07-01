from bs4 import BeautifulSoup, NavigableString, ResultSet, Tag
from selenium import webdriver
from datetime import datetime
import keyboard
from get_driver import get_driver
import os
import gc
import requests

# check_driver = os.path.isfile('browser_data.txt')
# if check_driver:
#     with open('browser_data.txt', 'r') as file:
#         driver = get_driver(file.read()[0], check_driver)
# else:
#     driver = get_driver('', False)

driver = webdriver.Firefox(executable_path="C:\\Program Files\\Mozilla Firefox\\geckodriver.exe")

# Writes found telegram tags/names or other key words to the file
def find_names(text:list)->None:
    with open('account_names.txt', 'a', encoding="utf-8") as file:
            for tag in text:
                if '@' in tag.text:
                    #print(f'Found tag by "@"! in message: {tag.text}')
                    file.write(tag.text.split('@')[1] + '\n')
                if 'ТГ' in tag.text:
                    #print(f'Found tag "ТГ"! in message: {tag.text}')
                    file.write(tag.text.split('ТГ')[1] + '\n')
                if 'тг' in tag.text:
                    #print(f'Found tag "тг"! in message: {tag.text}')
                    file.write(tag.text.split('тг')[1] + '\n')
                if 'Тг' in tag.text:
                    #print(f'Found tag "Тг"! in message: {tag.text}')
                    file.write(tag.text.split('Тг')[1] + '\n')
                if 'Телеграмм' in tag.text:
                    #print(f'Found tag "Телеграмм"! in message: {tag.text}')
                    file.write(tag.text.split('Телеграмм')[1] + '\n')
                if 'телеграм' in tag.text:
                    #print(f'Found tag "телеграм"! in message: {tag.text}')
                    file.write(tag.text.split('телеграм')[1] + '\n')
                if 'телега' in tag.text:
                    #print(f'Found tag "телега"! in message: {tag.text}')
                    file.write(tag.text.split('телега')[1] + '\n')
                if ' пиши ' in tag.text:
                    #print(f'Found tag "пиши"! in message: {tag.text}')
                    file.write(tag.text.split(' пиши ')[1] + '\n')
                if 'Пиши' in tag.text:
                    #print(f'Found tag "Пиши"! in message: {tag.text}')
                    file.write(tag.text.split('Пиши')[1] + '\n')

# Scrapes text on thread's page
def scrape_page(forum_posts:ResultSet)->None:
    text = []
    for post in forum_posts:
        text.append(post.find('div', { 'class' : 'bbWrapper'}))    
    find_names(text)

# Scrapes all pages in a thread
def scrape_thread()->bool:
    try:
        current_thread = driver.current_url
        soup = BeautifulSoup(requests.get(current_thread).text, 'html.parser')
        forum_posts = soup.find_all('article', class_="message-body js-selectToQuote")
        check_pagination = soup.find('ul', class_="pageNav-main")
        if check_pagination:
            check_same_ = Tag|NavigableString|None
            print(check_same_)
            for i in range(2,500):
                thread_soup = BeautifulSoup(requests.get(current_thread+f'page-{i}').text, "html.parser")
                check_same = thread_soup.find('article', class_="message-body js-selectToQuote")
                print(check_same)
                if check_same_ == check_same:
                    break
                else:
                    check_same_ = check_same
                    forum_posts = thread_soup.find_all('article', class_="message-body js-selectToQuote")
                    scrape_page(forum_posts)
        else:
            scrape_page(forum_posts)
        
        del(soup)
        del(check_pagination)
        del(forum_posts)
        gc.collect()
        if input('Continue?\nEnter [Y] to continue: ') == 'Y':
            scrape_thread()
        return False   
    except Exception as e:
        print(e)
        with open('error_log.txt', 'a') as log:
            log.write(f'{datetime.now()}\n{e}\n\n')
        driver.close()
        return False

def parse()->None:
    driver.get(input("Enter link to forum (preferably login): "))
    A = True
    while A:
        if keyboard.is_pressed("S"):
            A = scrape_thread()
    if input('Нажмите Enter что-бы закрыть окно браузера')+'a':
        driver.close()

parse()