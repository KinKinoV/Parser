from django.urls import path
from parser.views import *

urlpatterns = [
    path('', index, name='home'),
    path('savedTemps/', chooseFromSaved, name='chooseSaved'),
    path('tagData/', tagDataGet, name='newTags'),
    path('about/', about, name='about'),
    path('results/', resultPage, name='results'),
    path('search_user/', search_user, name='search_user'),
]

htmx_urlpatterns = [
    path('new_tag_field/', tagDataNewField, name='newTagField'),
]

urlpatterns += htmx_urlpatterns