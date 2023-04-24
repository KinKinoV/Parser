from django.urls import path
from parser.views import *
from parser.parser import loginReqCheck

urlpatterns = [
    path('', index, name='home'),
    path('savedTemps/', chooseFromSaved, name='chooseSaved'),
    path('tagData/', tagDataGet, name='newTags'),
    path('about/', about, name='about'),
    path('results/', resultPage, name='results'),
    path('parsing/', parsing, name='parsing')
]

htmx_urlpatterns = [
    path('new_tag_field/', tagDataNewField, name='newTagField'),
    path('start_parse/', startParse, name="startParse"),
    path('stop_parse/', stopParse, name="stopParse"),
    path('login_check/', loginReqCheck, name='loginCheck'),
    path('get_progress_text/', getProgressText, name="getProgressText")
]

urlpatterns += htmx_urlpatterns