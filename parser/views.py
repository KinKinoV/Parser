from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Q
from django.urls import reverse
from .parser import parse, kill_driver, SITE_MESSAGES
from .models import Forum, Nickname, BannedFilter, KeyWordFilter
import json
from threading import Thread


def index(request):
    return render(request, 'parser/index.html')

def chooseFromSaved(request):
    return render(request, 'parser/choose_from_saved.html')

def tagDataGet(request):

    if request.method == 'POST':
        regex_pattern = '/~/'
        message_parameter = {}
        pagination_parameter = {}
        thread_post_parameter = {}
        thread_link_parameter = {}
        main_page_theme_link_parameter = {}
        parameters_dict = [message_parameter, pagination_parameter, thread_post_parameter, thread_link_parameter, main_page_theme_link_parameter]
        parameters_names = ['message_parameter', 'pagination_parameter', 'thread_post_parameter', 'thread_link_parameter', 'main_page_theme_link_parameter']
        values = zip(parameters_dict, parameters_names)

        for parameter_dict, parameter_name in values:
            if request.POST.get(f'{parameter_name}2_name'):
                count = 1
                while request.POST.get(f'{parameter_name}{count}_name'):
                    if request.POST.get(f'{parameter_name}{count}_regex') == 'True':
                        parameter_dict[request.POST.get(f'{parameter_name}{count}_name')] = regex_pattern + request.POST.get(f'{parameter_name}{count}_value')
                    else:
                        parameter_dict[request.POST.get(f'{parameter_name}{count}_name')] = request.POST.get(f'{parameter_name}{count}_value')
                    count += 1
            else:   
                if request.POST.get(f'{parameter_name}1_regex') == 'True':
                    parameter_dict[request.POST.get(f'{parameter_name}1_name')] = regex_pattern + request.POST.get(f'{parameter_name}1_value')
                else:
                    parameter_dict[request.POST.get(f'{parameter_name}1_name')] = request.POST.get(f'{parameter_name}1_value')
        
        data_to_pass = {
            'message_tag' : request.POST.get('message_tag'),
            'message_parameter' : message_parameter,
            'pagination_tag' : request.POST.get('pagination_tag'),
            'pagination_parameter' : pagination_parameter,
            'thread_post_tag' : request.POST.get('thread_post_tag'),
            'thread_post_parameter' : thread_post_parameter,
            'thread_link_tag' : request.POST.get('thread_link_tag'),
            'thread_link_parameter' : thread_link_parameter,
            'main_page_theme_link_tag': request.POST.get('main_page_theme_link_tag'),
            'main_page_theme_link_parameter': main_page_theme_link_parameter,
            'pagination_case' : request.POST.get('paginationCase'),
            'pagination_template' : request.POST.get('paginationTemplate'),
            'page_load_delay' : request.POST.get('pageLoadDelay')
        }
        if data_to_pass['pagination_case'] == 'C':
            data_to_pass['thread_step'] = request.POST.get('threadStep')
            data_to_pass['forum_step'] = request.POST.get('forumStep')
        
        if request.POST.get('botProtection') == 'True':
            data_to_pass['bot_protection'] = 'True'
        else:
            data_to_pass['bot_protection'] = 'False'

        if request.POST.get('loginRequirment') == 'True':
            data_to_pass['login_requirment'] = 'True'
        else:
            data_to_pass['login_requirment'] = 'False'

        forumTemplate = Forum(link=request.POST.get('forumLink'), parseConfigs = json.dumps(data_to_pass))
        forumTemplate.save()
        return HttpResponseRedirect('/')
    
    return render(request, 'parser/tag_data.html')

def about(request):
    return render(request, 'parser/about.html')

def resultPage(request):
    p = Paginator(Nickname.objects.all(), 100)
    page = request.GET.get('page')
    users = p.get_page(page)
    users.adjusted_elided_pages = p.get_elided_page_range(page)
    forums=(set(Nickname.objects.values_list('forumOrigin',flat=True)))
    context = {
        'users': users,
        'nums': range(users.paginator.num_pages),
        'forums': forums,
    }
    return render(request, 'parser/results.html', context)

def parsing(request):
    context = {
        'forums': Forum.objects.all().order_by('link'),
        'filters' : BannedFilter.objects.all().order_by('purpose'),
    }

    if request.method == 'PATCH':
        return render(request, 'parser/partials/parsingForm.html', context)
    
    return render(request, 'parser/parse_page.html', context)

# ============================================[ HTMX functions ]============================================ #
def tagDataNewField(request):
    if request.method == 'GET':
        parameter = request.GET.get('parameter')
        value = int(request.GET.get('value'))
        swapId = {
            'message': 1,
            'pagination': 2,
            'thread_post': 3,
            'thread_link': 4,
            'main_page_theme_link': 5,
            }
        context = {
            'parameterName' : parameter, 
            'value': value, 
            'idNum': swapId[parameter]
        }
        return render(request, 'parser/partials/formField.html', context)

def startParse(request):
    context = {}
    if request.method == 'POST':
        link = request.POST.get('linkSelect')
        resultFilter = request.POST.get('filterSelect')
        # Обязательно name в будущем сделать с учётом присутствия нескольких пользователей
        Thread(target=parse, args=[link, resultFilter], name='ParserThread').start()
        if '"login_requirment": "True"' in Forum.objects.get(link=link).parseConfigs:
            context['login_check'] = True
        return render(request, 'parser/partials/stopButton.html', context)

def stopParse(request):
    if request.method == "PATCH":
        kill_driver()
        context = {
            'forums': Forum.objects.all().order_by('link'),
            'filters' : BannedFilter.objects.all().order_by('purpose')
        }
        return render(request, 'parser/partials/parsingForm.html', context)
    
def getProgressText(request):
    text_to_pass = ''
    if request.method == "GET":
        if not len(SITE_MESSAGES) == 0:
            for msg in SITE_MESSAGES:
                if msg == "Остановка скрипта...":
                    context = {
                        'forums': Forum.objects.all().order_by('link'),
                        'filters' : BannedFilter.objects.all().order_by('purpose')
                    }
                    return render(request, 'parser/partials/parsingForm.html', context)
                else:
                    text_to_pass += msg + '<br>'
            return HttpResponse(f"{text_to_pass}")
        else:
            return HttpResponse("")

def search_user(request):      
    search_text = request.POST.get('search')
    forum_of_origin = request.POST.get('forumfilter')
    if search_text == "" and forum_of_origin == "":
        response = HttpResponse("")
        response["HX-Redirect"] = reverse("results")
        return response
    else:
        final_results =  Nickname.objects.filter(Q(forumOrigin__link__icontains=forum_of_origin)&Q(handler__icontains=search_text)).order_by('id')
        forums=(set(Nickname.objects.values_list('forumOrigin',flat=True)))
        context = {
            'forums':forums,
            'search_results':final_results,
            }
        return render(request, 'parser/partials/search_results.html', context)

def delete_handler(request, id):
    if request.method == "GET":
        Nickname.objects.filter(pk=id).delete()
        return HttpResponse()

def add_to_keys(request, id):
    if request.method == "GET":
        key_word_db = KeyWordFilter.objects.get(purpose='Telegram')
        key_word_db.filter += '\n' + Nickname.objects.get(pk=id).handler
        key_word_db.save()
        Nickname.objects.get(pk=id).delete()
        return HttpResponse()

def add_to_banned(request, id):
    if request.method == "GET":
        banned_word_db = BannedFilter.objects.get(purpose='Telegram')
        banned_word_db.filter += '\n' + Nickname.objects.get(pk=id).handler
        banned_word_db.save()
        Nickname.objects.filter(pk=id).delete()
        return HttpResponse()