from django.urls import path
from . import views

urlpatterns = [
    #path('register_user',views.signUp.as_view(), name='register_user'),
    path('register_user',views.register_user, name='register_user'),
    path('login/', views.logIn.as_view(), name="login"),
    path('logout/', views.logOut.as_view(), name="logout"),  
]