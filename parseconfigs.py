import json
import re

class Xceref:
    type_ = 'Xceref'
    message_tag = 'div'
    message_parameter = {'class': 'bbWrapper'}
    pagination_tag = 'ul'
    pagination_parameter = {'class' : 'pageNav-main'}
    thread_post_tag = 'article'
    thread_post_parameter ={'class' : 'message-body js-selectToQuote'} 
    forum_threads_tag = 'div'
    forum_threads_parameter = {'class' : 'structItem-title'}
    s_word_flag = False
    thread_link_pos = 2
    pagination_case = 'I'
    pagination_template = 'page-{}'
    bot_protection = False
    page_load_delay = 0

class phpBB:
    type_ = 'phpBB'
    message_tag = 'div'
    message_parameter = {'class' : 'content'}
    pagination_tag = 'div'
    pagination_parameter = {'class':'pagination'}
    thread_post_tag = 'div'
    thread_post_parameter ={'class' : 'postbody'} 
    forum_threads_tag = 'dt'
    forum_threads_parameter = {}
    forum_step = 25
    thread_step = 15
    s_word_flag = False
    thread_link_pos = int()
    pagination_case = 'C'
    pagination_template = '&start={}'
    bot_protection = False
    page_load_delay = 0

    def __init__(self) -> None:
        self.forum_threads_parameter[input("Enter name of thread body parameter: ")] = input("Enter value of a thread body parameter: ")

class OtherSoft:
    type_ = 'Other'
    message_tag = str()
    message_parameter = {}
    pagination_tag = str()
    pagination_parameter = {}
    thread_post_tag = str()
    thread_post_parameter = {}
    forum_threads_tag = str()
    forum_threads_parameter = {}

    def __init__(self):
        with open('data\\other_soft_tags.txt', 'r', encoding='utf-8') as file:
            tags = json.load(file)
            regex_pattern = '/~/'

            self.message_tag = tags['message_tag']
            for key, value in tags['message_parameter'].items():
                if regex_pattern in value:
                    self.message_parameter[key] = re.compile(value.strip(regex_pattern))
                else:
                    self.message_parameter[key] = value

            self.pagination_tag = tags['pagination_tag']
            for key, value in tags['pagination_parameter'].items():
                if regex_pattern in value:
                    self.pagination_parameter[key] = re.compile(value.strip(regex_pattern))
                else:
                    self.pagination_parameter[key] = value

            self.thread_post_tag = tags['thread_post_tag']
            for key, value in tags['thread_post_parameter'].items():
                if regex_pattern in value:
                    self.thread_post_parameter[key] = re.compile(value.strip(regex_pattern))
                else:
                    self.thread_post_parameter[key] = value
            
            self.forum_threads_tag = tags['forum_threads_tag']
            for key, value in tags['forum_threads_parameter'].items():
                if regex_pattern in value:
                    self.forum_threads_parameter[key] = re.compile(value.strip(regex_pattern))
                else:
                    self.forum_threads_parameter[key] = value