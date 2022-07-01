from selenium import webdriver

def get_driver(name:str, check_file:bool):
    if check_file:
        if name == 'chrome' or name == 'Chrome' or name == 'Google chrome':
            with open('browser_data.txt', 'r'):
                pass
            return webdriver.Chrome(executable_path=input('Enter path to chromedrive(change \ to \\ ): '))
        if name == 'firefox' or name == 'Firefox' or name == 'Mozilla Firefox' or name == 'mozilla' or name == 'Mozilla':
            return webdriver.Firefox(executable_path=input('Enter path to geckodriver(change \ to \\ ):'))
    else:
        with open('browser_path.txt', 'w') as file:
            file.write(input('Enter path to your browser driver: '))
        get_driver(name)