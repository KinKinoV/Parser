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
    s_word_flag = True
    s_word = '/forums'
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
        self.message_tag = input("Enter tag where a post's text is: ")
        for i in range(int(input(f'How many parameters in a {self.message_tag} tag? '))):
            if input("Do you need regular expressions for this tag? ") == 'Y':
                self.message_parameter[input(f'Enter parameter {i+1} name: ')] = re.compile(input(f'Enter parameter {i+1} value: '))
            else:
                self.message_parameter[input(f'Enter parameter {i+1} name: ')] = (input(f'Enter parameter {i+1} value: '))
        self.pagination_tag = input("Enter tag of the pagination module: ")
        for i in range(int(input(f'How many parameters in a {self.pagination_tag} tag? '))):
            if input("Do you need regular expressions for this tag? ") == 'Y':
                self.pagination_parameter[input(f'Enter parameter {i+1} name: ')] = re.compile(input(f'Enter parameter {i+1} value: '))
            else:
                self.pagination_parameter[input(f'Enter parameter {i+1} name: ')] = input(f'Enter parameter {i+1} value: ')
        self.thread_post_tag = input("Enter tag of the forum's post body: ")
        for i in range(int(input(f'How many parameters in a {self.thread_post_tag} tag? '))):
            if input("Do you need regular expressions for this tag? ") == 'Y':
                self.thread_post_parameter[input(f'Enter parameter {i+1} name: ')] = re.compile(input(f'Enter parameter {i+1} value: '))
            else:
                self.thread_post_parameter[input(f'Enter parameter {i+1} name: ')] = input(f'Enter parameter {i+1} value: ')
        self.forum_threads_tag = input("Enter tag of the thread's body on forum: ")
        for i in range(int(input(f'How many parameters in a {self.forum_threads_tag} tag? '))):
            if input("Do you need regular expressions for this tag? ") == 'Y':
                self.forum_threads_parameter[input(f'Enter parameter {i+1} name: ')] = re.compile(input(f'Enter parameter {i+1} value: '))
            else:
                self.forum_threads_parameter[input(f'Enter parameter {i+1} name: ')] = input(f'Enter parameter {i+1} value: ')