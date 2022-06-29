from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time

username = input("Enter username: ")
password = input("Enter password: ")

driver = webdriver.Firefox(executable_path="C:\\Program Files\\Mozilla Firefox\\geckodriver.exe")
driver.get(input("Enter link to forum login: "))

def main():
    driver.find_element(By.NAME, input("Enter name of 'username' field: ")).send_keys(username)

    driver.find_element(By.NAME, input("Enter name of 'password' field: ")).send_keys(password)

    driver.find_element(By.NAME, input("Enter class name of button field to login: ")).click()

    #driver.close()

if input():
    main()