from django.urls import path
from parser.views import *
from parser.parser import loginReqCheck

urlpatterns = [
    path('', index, name='home'),
    path('savedTemps/', chooseFromSaved, name='chooseSaved'),
    path('tagData/', tagDataGet, name='newTags'),
    path('about/', about, name='about'),
    path('results/', resultPage, name='results'),
    path('parsing/', parsing, name='parsing'),
    path('search_user/', search_user, name='search_user'),
    path('save_search_csv/', save_search_results, name='save_search_csv'),
    path('save_search_excel/', save_as_excel, name='save_search_excel'),
]

htmx_urlpatterns = [
    path('new_tag_field/', tagDataNewField, name='newTagField'),
    path('start_parse/', startParse, name="startParse"),
    path('stop_parse/', stopParse, name="stopParse"),
    path('login_check/', loginReqCheck, name='loginCheck'),
    path('get_progress_text/', getProgressText, name="getProgressText"),
    path('delete_handler/<int:id>/', delete_handler, name="delete"),
    path('add_to_keys/<int:id>/', add_to_keys, name="add_key"),
    path('add_to_banned/<int:id>/', add_to_banned, name="add_banned"),
]

urlpatterns += htmx_urlpatterns