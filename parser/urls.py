from django.urls import path
from parser.views import *

urlpatterns = [
    path('', index, name='home'),
    path('savedTemps/', chooseFromSaved, name='chooseSaved'),
    path('tagData/', tagDataGet, name='newTags'),
    path('about/', about, name='about') 
]

htmx_urlpatterns = [
    path('new_tag_field/', tagDataNewField, name='newTagField')
]

urlpatterns += htmx_urlpatterns