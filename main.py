from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
import re
import keyboard
from get_driver import get_driver
import os

check_file = os.path.isfile('browser_data.txt')
driver = get_driver(input('Enter name of your browser: '), check_file)

def loop():
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        forum_posts = soup.find_all('article', class_="message-body js-selectToQuote")
        text = []
        for post in forum_posts:
            text.append(post.find('div', { 'class' : 'bbWrapper'}))
            
        with open('account_names.txt', 'a', encoding="utf-8") as file:
            for tag in text:
                if '@' in tag.text:
                    print(f'Found tag by "@"! in message: {tag.text}')
                    file.write(tag.text.split('@')[1] + '\n')
                if 'ТГ' in tag.text:
                    print(f'Found tag "ТГ"! in message: {tag.text}')
                    file.write(tag.text.split('ТГ')[1] + '\n')
                if 'тг' in tag.text:
                    print(f'Found tag "тг"! in message: {tag.text}')
                    file.write(tag.text.split('тг')[1] + '\n')
                if 'Тг' in tag.text:
                    print(f'Found tag "Тг"! in message: {tag.text}')
                    file.write(tag.text.split('Тг')[1] + '\n')
                if 'Телеграмм' in tag.text:
                    print(f'Found tag "Телеграмм"! in message: {tag.text}')
                    file.write(tag.text.split('Телеграмм')[1] + '\n')
                if 'телеграм' in tag.text:
                    print(f'Found tag "телеграм"! in message: {tag.text}')
                    file.write(tag.text.split('телеграм')[1] + '\n')
                if 'телега' in tag.text:
                    print(f'Found tag "телега"! in message: {tag.text}')
                    file.write(tag.text.split('телега')[1] + '\n')
                if ' пиши ' in tag.text:
                    print(f'Found tag "пиши"! in message: {tag.text}')
                    file.write(tag.text.split(' пиши ')[1] + '\n')
                if 'Пиши' in tag.text:
                    print(f'Found tag "Пиши"! in message: {tag.text}')
                    file.write(tag.text.split('Пиши')[1] + '\n')
        if input('Continue?\nEnter [Y] to continue: ') == 'Y':
            loop()
        return False
            
    except Exception as e:
        print(e)
        with open('error_log.txt', 'a') as log:
            log.write(f'{datetime.now()}\n{e}\n\n')
        driver.close()
        return False

def parse():
    driver.get(input("Enter link to forum (preferably login): "))
    
    A = True
    while A:
        if keyboard.is_pressed("S"):
            A = loop()
    
    if input('Нажмите Enter что-бы закрыть окно браузера')+'a':
        driver.close()

if __name__ == "__main__":
    parse()