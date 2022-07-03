from selenium import webdriver

def get_driver(name:str, check_file:bool):
    if check_file:
        with open('browser_data.txt', 'r') as file:
            if name == 'chrome' or name == 'Chrome' or name == 'Google chrome':
                return webdriver.Chrome(executable_path=file.read()[1])
            if name == 'firefox' or name == 'Firefox' or name == 'Mozilla Firefox' or name == 'mozilla' or name == 'Mozilla':
                return webdriver.Firefox(executable_path=file.read()[1])
    else:
        with open('browser_data.txt', 'w') as file:
            file.write(f"{input('Enter browser name: ')}\n{input('Enter path to your browser driver(geckodriver, chromedriver, etc.): ')}")
        with open('browser_data.txt', 'r') as file:
            name = file.read()[0]
        get_driver(name, True)