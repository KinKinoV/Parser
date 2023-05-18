from django.urls import path
from . import views

urlpatterns = [
    #path('register_user',views.signUp.as_view(), name='register_user'),
    path('register_user',views.register_user, name='register_user'),
    path('login/', views.logIn.as_view(), name="login"),
    path('logout/', views.logOut.as_view(), name="logout"),
    path('admin_approval/', views.admin_approval, name="admin-approval"),
    path('admin_approval/search_user/', views.search_user, name="admin_search_user"),  
]

htmx_urlpatterns = [
    path('add_staff/<str:nickname>/', views.add_staff, name="add_staff"),
    path('remove_staff/<str:nickname>/', views.remove_staff, name="remove_staff"),
    path('delete_user/<str:nickname>/', views.delete_user,name="delete_user"),
]

urlpatterns += htmx_urlpatterns