from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm,UserChangeForm,PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from .forms import RegisterUserForm,EditSettingsForm,PasswordChangingForm, LoginUserForm
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import DetailView,CreateView
from django.db.models import Q
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.


def register_user(request):
    registred = False
    if request.user.is_superuser:
        if request.method=="POST":
            form = RegisterUserForm(request.POST)
            if form.is_valid():
                user = form.save()
                registred = True
                messages.success(request,("Registration were successful"))
                return redirect('about')
        else:
            form = RegisterUserForm()
        return render(request,'authenticate/register_user.html',{
            'form':form,
            })
    else:
        messages.warning(request,("You have no rights to register"))
        return redirect('about')

# class signUp(SuccessMessageMixin, generic.CreateView):
#     form_class = RegisterUserForm
#     template_name = "authenticate/register_user.html"
#     success_url = reverse_lazy('about')
#     success_message = "User has been created, please login with your username and password"

#     def form_invalid(self, form):
#         messages.add_message(self.request, messages.ERROR,
#                              "Please enter details properly")
#         return redirect('about')
    
#     def check_superuser(self,request):
#         if request.user.is_superuser:
#             pass
#         else:
#             return redirect('about')
            

class logIn(generic.View):
    form_class = LoginUserForm
    template_name = "authenticate/login.html"

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if request.method == "POST":
            form = LoginUserForm(request, data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')

                user = authenticate(username=username, password=password)

                if user is not None:
                    login(request, user)
                    messages.success(
                        request, f"You are logged in as {username}")
                    return redirect('home')
                else:
                    messages.error(request, "Error")
            else:
                messages.error(request, "Username or password incorrect")
        form = LoginUserForm()
        return render(request, "authors/login.html", {"form": form})

class logOut(LoginRequiredMixin, generic.View):
    login_url = 'login'

    def get(self, request):
        logout(request)
        messages.success(request, "User logged out")
        return redirect('about')
# def register_user(request):
#     registred = False
#     if request.method=="POST":
#         form = RegisterUserForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             messages.success(request,("Registration were successful"))
#             return redirect('about')
#     else:
#         form = RegisterUserForm()
#     return render(request,'authenticate/register_user.html',{
#         'form':form,
#         })