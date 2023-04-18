from django.shortcuts import render
from .models import Forum
import json

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
            'thread_link_parameter' : thread_link_parameter
        }
        forumTemplate = Forum(link="https://someotherforum.com", parseConfigs = json.dumps(data_to_pass))
        forumTemplate.save()
    return render(request, 'parser/tag_data.html')

def about(request):
    return render(request, 'parser/about.html')


# HTMX functions
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