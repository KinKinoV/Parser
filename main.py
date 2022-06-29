from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import time

username = input("Enter username: ")
password = input("Enter password: ")

driver = webdriver.Firefox(executable_path="C:\\Program Files\\Mozilla Firefox\\geckodriver.exe")
driver.get(input("Enter link to forum login: "))

def main():
    driver.find_element_by_id(input("Enter id of 'username' field: ")).send_keys(username)

    driver.find_element_by_id(input("Enter id of 'password' field: ")).send_keys(password)

    driver.find_element_by_name(input("Enter class name of button to login: ")).click()

    #driver.close()

if input():
    main()