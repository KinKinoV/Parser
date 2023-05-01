from typing import final
from django.shortcuts import render
from django.core.paginator import Paginator, Page
from django.http import HttpResponseRedirect, HttpResponse
from threading import Thread
from .parser import parse, kill_parse, SITE_MESSAGES, PARSER_WORK
from .models import Forum, Nickname, BannedFilter
import json
from django.db.models import Q

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
        parameters_dict = [message_parameter, pagination_parameter, thread_post_parameter, thread_link_parameter]
        parameters_names = ['message_parameter', 'pagination_parameter', 'thread_post_parameter', 'thread_link_parameter']
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

def otherData(request):
    return render(request, 'parser/other_data.html')

def about(request):
    return render(request, 'parser/about.html')

def resultPage(request):
    p = Paginator(Nickname.objects.all(), 100)
    page = request.GET.get('page')
    users = p.get_page(page)
    nums = ""*users.paginator.num_pages
    forums=(set(Nickname.objects.values_list('forumOrigin',flat=True)))
    context = {
        'users': users,
        'nums': nums,
        'forums':forums,
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

def save_result(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=result_user.csv'
    writer = csv.writer(response)
    writer.writerow(['Id','Handler','Telegram Id','Nicknames','Forum of origin',])
    users=Nickname.objects.all()
    for user in users:
        writer.writerow([user.id, user.handler, user.user_id, user.nicknames, user.forumOrigin,])
    return response

def save_search_results(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=result_user.csv'
    writer = csv.writer(response)
    writer.writerow(['Id','Handler','Telegram Id','Nicknames','Forum of origin',])
    with open('bufferSearch.txt', 'r') as f:
        txt=f.read()
        components=txt.split(',')
        search_text = components[0]
        forum_of_origin = components[1]
    user_results =  Nickname.objects.filter(Q(forumOrigin__link__icontains=forum_of_origin)&Q(handler__icontains=search_text)).order_by('id')
    for user in user_results:
            writer.writerow([user.id, user.handler, user.user_id, user.nicknames, user.forumOrigin,])
    return response
    

# ============================================[ HTMX functions ]============================================ #
def tagDataNewField(request):
    if request.method == 'GET':
        parameter = request.GET.get('parameter')
        value = int(request.GET.get('value'))
        swapId = {
            'message': 1,
            'pagination': 2,
            'thread_post': 3,
            'thread_link': 4
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
        toParse = request.POST.get('linksToParse')
        resultFilter = request.POST.get('filterSelect')
        # Обязательно name в будущем сделать с учётом присутствия нескольких пользователей
        Thread(target=parse, args=[link, toParse, resultFilter], name='ParserThread').start()
        if '"login_requirment": "True"' in Forum.objects.get(link=link).parseConfigs:
            context['login_check'] = True
        return render(request, 'parser/partials/stopButton.html', context)

def stopParse(request):
    if request.method == "PATCH":
        kill_parse()
        context = {
            'forums': Forum.objects.all().order_by('link'),
            'filters' : BannedFilter.objects.all().order_by('purpose')
        }
        return render(request, 'parser/partials/parsingForm.html', context)
    
def getProgressText(request):
    if request.method == "GET":
        if SITE_MESSAGES == []:
            text_to_pass = "No messages"
        else:
            text_to_pass = SITE_MESSAGES[len(SITE_MESSAGES)-1]
        return HttpResponse(f"{text_to_pass}")

def search_user(request):      
    search_text = request.POST.get('search')
    forum_of_origin = request.POST.get('forumfilter')
    if search_text == None and forum_of_origin == None:
        with open('bufferSearch.txt', 'r') as f:
            txt=f.read()
            components=txt.split(',')
            search_text = components[0]
            forum_of_origin = components[1]
    final_results =  Nickname.objects.filter(Q(forumOrigin__link__icontains=forum_of_origin)&Q(handler__icontains=search_text)).order_by('id')
    with open('bufferSearch.txt','w') as f:
        f.write(f'{search_text},{forum_of_origin}')
    p = Paginator(final_results, 100)
    page = request.GET.get('spage')
    search_users = p.get_page(page)
    search_nums = ""*search_users.paginator.num_pages
    forums=(set(Nickname.objects.values_list('forumOrigin',flat=True)))
    context = {
        'forums':forums,
        'search_results':final_results,
        'search_users': search_users,
        'search_nums': search_nums,
        }
    return render(request, 'parser/partials/search_results.html', context)