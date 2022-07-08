from enum import Enum

class Xceref(Enum):
    message_tag = 'div'
    message_class = 'bbWrapper'
    pagination_tag = 'ul'
    pagination_class = 'pageNav-main'
    thread_post_tag = 'article'
    thread_post_class = 'message-body js-selectToQuote'
    forum_threads_tag = 'div'
    forum_threads_class = 'structItem-title'

class phpBB(Enum):
    message_tag = 'div'
    message_class = 'content'
    pagination_tag = 'div'
    pagination_class = 'pagination'
    thread_post_tag = 'div'
    thread_post_class = 'postbody'
    forum_threads_tag = 'dt'