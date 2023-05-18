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
from django.core.paginator import Paginator

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
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


def admin_approval(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            user_count=User.objects.all().count()
            users=User.objects.all().exclude(is_superuser=True).order_by('username')
            # users_all_ids=[]
            # approved_users=[]
            # for i in range(0,len(users),1):
            #     if users[i].is_staff:
            #         approved_users.append(str(users[i].id))
            # for i in range(0,len(users),1):
            #     users_all_ids.append(str(users[i].id))
            # if request.method=="POST":
            #     id_list_approve=request.POST.getlist('boxes')

            #     User.objects.filter(id__in=id_list_approve).update(is_staff=True)
            #     User.objects.exclude(id__in=id_list_approve).update(is_staff=False)
                
            #     # all_approved = id_list_approve + approved_users
            #     # for item in all_approved:
            #     #     User.objects.filter(pk=int(item)).update(is_staff=True)
            #     # id_set_disaprove = set(users_all_ids)-set(all_approved)
            #     # id_list_disaprove=list(id_set_disaprove)
            #     # for y in id_list_disaprove:
            #     #     User.objects.filter(pk=int(y)).update(is_staff=False)
            #     messages.success(request,("User were promoted"))
            #     return redirect('admin-approval')
            # else:
            p = Paginator(users, 20)
            page=request.GET.get('page')
            uspage=p.get_page(page)
            nums=""*uspage.paginator.num_pages
            return render(request,'authenticate/admin_approval.html',
                    {
                        'user_count':user_count,
                        'users':users,
                        'nums':nums,   
                        'uspage':uspage,     
                    })
        else:
            messages.success(request,("You are not authorized"))
            return redirect('about')
    else:
        messages.success(request,("You are not authorized"))
        return redirect('about')

def search_user(request):
    if not request.user.is_superuser:
        return redirect('about')   
    search_text = request.POST.get('search')
    if search_text == None:
        search_text = ''
    results =  User.objects.filter(username__icontains=search_text).order_by('id')
    context = {
        'search_results':results,
        'search_text':search_text,
        }
    return render(request, 'authenticate/search_results.html', context)

# ============================================[ HTMX functions ]============================================ #
    
def remove_staff(request, nickname):
    if not request.user.is_authenticated:
        return redirect('about')
    if request.method == "GET":
        User.objects.filter(username=nickname).update(is_staff=False)
        response = HttpResponse("Okay")
        response["HX-Redirect"] = reverse("admin-approval") + f"?page={request.GET.get('page')}"
        return response

def add_staff(request, nickname):
    if not request.user.is_authenticated:
        return redirect('about')
    if request.method == "GET":
        User.objects.filter(username=nickname).update(is_staff=True)
        response = HttpResponse("Okay")
        response["HX-Redirect"] = reverse("admin-approval") + f"?page={request.GET.get('page')}"
        return response

def delete_user(request, nickname):
    if not request.user.is_superuser:
        return redirect('about')
    if request.method == "GET":
        User.objects.filter(username=nickname).delete()
        response = HttpResponse("Okay")
        response["HX-Redirect"] = reverse("admin-approval") + f"?page={request.GET.get('page')}"
        return response