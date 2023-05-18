from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Q
from django.urls import reverse
from django.contrib import messages
from .parser import parse, kill_parse, SITE_MESSAGES
from .models import Forum, Nickname, BannedFilter, KeyWordFilter
import json
from threading import Thread


from pandas import DataFrame, ExcelWriter
import csv

def index(request):
    return render(request, 'parser/index.html')

def chooseFromSaved(request):
    if not request.user.is_authenticated:
        return redirect('about')
    return render(request, 'parser/choose_from_saved.html')

def tagDataGet(request):
    if not request.user.is_authenticated:
        return redirect('about')
        
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
    if not request.user.is_authenticated:
        return redirect('about')
    p = Paginator(Nickname.objects.all(), 100)
    page = request.GET.get('page')
    users = p.get_page(page)
    nums = ""*users.paginator.num_pages
    forums=(set(Nickname.objects.values_list('forumOrigin',flat=True)))
    context = {
        'users': users,
        'nums': nums,
        'forums': forums,
    }
    return render(request, 'parser/results.html', context)

def parsing(request):
    if not request.user.is_authenticated:
        return redirect('about')
    context = {
        'forums': Forum.objects.all().order_by('link'),
        'filters' : BannedFilter.objects.all().order_by('purpose'),
    }

    if request.method == 'PATCH':
        return render(request, 'parser/partials/parsingForm.html', context)
    
    
    return render(request, 'parser/parse_page.html', context)

def save_result(request):
    if not request.user.is_authenticated:
        return redirect('about')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=result_user.csv'
    writer = csv.writer(response)
    writer.writerow(['Id','Handler','Telegram Id','Nicknames','Forum of origin',])
    users=Nickname.objects.all()
    for user in users:
        writer.writerow([user.id, user.handler, user.user_id, user.nicknames, user.forumOrigin,])
    return response

def save_search_results(request):
    if not request.user.is_authenticated:
        return redirect('about')
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


def save_as_excel(request):
    if not request.user.is_authenticated:
        return redirect('about')
    forums=(set(Forum.objects.values_list('link')))
    forumlist={}
    response = HttpResponse(content_type='text/xslx')
    response['Content-Disposition'] = 'attachment; filename=result_user.xlsx'
    writer = ExcelWriter(response)
    users=Nickname.objects.all()
    for user in users:
        for forum in forums:
            if str(user.forumOrigin) in str(forum):
                name = user.forumOrigin.link.replace('/', '')
                name = name.replace('http:', '')
                name = name.replace('https:', '')
                try:
                    forumlist[f'{name}'].append([user.handler, user.nicknames])
                except:
                    newadd={f'{name}':[[user.handler, user.nicknames]]}
                    forumlist.update(newadd)
    for list in forumlist:
        DataFrame(forumlist[list]).to_excel(writer,sheet_name=f'{list}',index=False)
    writer.save()                   
    return response
#save_search_excel
                
                
            
        
    
    
    

# ============================================[ HTMX functions ]============================================ #
def tagDataNewField(request):
    if not request.user.is_authenticated:
        return redirect('about')
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
    if not request.user.is_authenticated:
        return redirect('about')
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
    if not request.user.is_authenticated:
        return redirect('about')
    if request.method == "PATCH":
        kill_parse()
        context = {
            'forums': Forum.objects.all().order_by('link'),
            'filters' : BannedFilter.objects.all().order_by('purpose')
        }
        return render(request, 'parser/partials/parsingForm.html', context)
    
def getProgressText(request):
    if not request.user.is_authenticated:
        return redirect('about')
    text_to_pass = ''
    if request.method == "GET":
        if not len(SITE_MESSAGES) == 0:
            for msg in SITE_MESSAGES:
                text_to_pass += msg + '<br>'
            return HttpResponse(f"{text_to_pass}")
        else:
            return HttpResponse("")

def search_user(request):
    if not request.user.is_authenticated:
        return redirect('about')      
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
    if not request.user.is_authenticated:
        return redirect('about')
    if request.method == "GET":
        Nickname.objects.filter(pk=id).delete()
        response = HttpResponse("Okay")
        response["HX-Redirect"] = reverse("results") + f"?page={request.GET.get('page')}"
        return response

def add_to_keys(request, id):
    if not request.user.is_authenticated:
        return redirect('about')
    if request.method == "GET":
        key_word_db = KeyWordFilter.objects.get(purpose='Telegram')
        key_word_db.filter += '\n' + Nickname.objects.get(pk=id).handler
        key_word_db.save()
        Nickname.objects.get(pk=id).delete()
        response = HttpResponse("Okay")
        response["HX-Redirect"] = reverse("results") + f"?page={request.GET.get('page')}"
        return response

def add_to_banned(request, id):
    if not request.user.is_authenticated:
        return redirect('about')
    if request.method == "GET":
        banned_word_db = BannedFilter.objects.get(purpose='Telegram')
        banned_word_db.filter += '\n' + Nickname.objects.get(pk=id).handler
        banned_word_db.save()
        Nickname.objects.filter(pk=id).delete()
        response = HttpResponse("Okay")
        response["HX-Redirect"] = reverse("results") + f"?page={request.GET.get('page')}"
        return response