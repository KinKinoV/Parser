import json
import re

class ParseSettings:
    message_tag = str
    message_parameter = {}
    pagination_tag = str
    pagination_parameter = {}
    thread_post_tag = str
    thread_post_parameter = {}
    forum_threads_tag = str
    forum_threads_parameter = {}
    forum_step = int
    thread_step = int
    pagination_case = str
    pagination_template = str
    bot_protection = False
    page_load_delay = int
    search_string = str
    forum_link = str
    login_requirment = False


    def __init__(self):
        with open('data\\parse_configs.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            regex_pattern = '/~/'

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
            
            self.forum_threads_tag = data['forum_threads_tag']
            for key, value in data['forum_threads_parameter'].items():
                if regex_pattern in value:
                    self.forum_threads_parameter[key] = re.compile(value.strip(regex_pattern))
                else:
                    self.forum_threads_parameter[key] = value

            self.pagination_case = data['pagination_case']
            
            if self.pagination_case == 'C':
                self.forum_step = int(data['forum_step'])
                self.thread_step = int(data['thread_step'])
            
            self.pagination_template = data['pagination_template']
            
            if data['bot_protection'] == 'True':
                self.bot_protection = True
            
            self.page_load_delay = int(data['page_load_delay'])
            # Temporary, later will be loaded from file too
            self.search_string = '.\\B(?=\\w{5,32}\\b)[a-zA-Z0-9]+(?:_[a-zA-Z0-9]+)*'
            self.forum_link = data['forum_link']

            if data['login_requirment'] == 'True':
                self.login_requirment = True
