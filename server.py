from msilib.schema import File
from flask import Flask, request, render_template, redirect, url_for
import json

app = Flask(__name__)
app.jinja_env.globals['static'] = (
    lambda filename : url_for('static', filename=filename)
)

def start():
    app.run(host='0.0.0.0', debug=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    # Main page
    return render_template('index.html')


@app.route('/tag_definition/<mp_amm>/<pp_amm>/<tp_amm>/<ftp_amm>', methods=["GET", "POST"])
def get_tag_definition(mp_amm = 1, pp_amm = 1, tp_amm = 1, ftp_amm = 1):
    if request.method == 'POST':
        regex_pattern = '/~/'
        message_parameter = {}
        pagination_parameter = {}
        thread_post_parameter = {}
        forum_threads_parameter = {}
        counters = [mp_amm, pp_amm, tp_amm, ftp_amm]
        parameters_dict = [message_parameter, pagination_parameter, thread_post_parameter, forum_threads_parameter]
        parameters_names = ['message_parameter', 'pagination_parameter', 'thread_post_parameter', 'forum_threads_parameter']
        values_ = zip(counters, parameters_dict, parameters_names)

        for count, parameter_dict, parameter_name in values_:
            if count == '1':
                if request.form.get(f'{parameter_name}{0}_regex') == 'True':
                    parameter_dict[request.form.get(f'{parameter_name}{0}_name')] = regex_pattern + request.form.get(f'{parameter_name}{0}_value')
                else:
                    parameter_dict[request.form.get(f'{parameter_name}{0}_name')] = request.form.get(f'{parameter_name}{0}_value')
            else:
                for i in range(int(count)):    
                    if request.form.get(f'{parameter_name}{i}_regex') == 'True':
                        parameter_dict[request.form.get(f'{parameter_name}{i}_name')] = regex_pattern + request.form.get(f'{parameter_name}{i}_value')
                    else:
                        parameter_dict[request.form.get(f'{parameter_name}{i}_name')] = request.form.get(f'{parameter_name}{i}_value')
        
        data_to_pass = {
            'message_tag' : request.form.get('message_tag'),
            'message_parameter' : message_parameter,
            'pagination_tag' : request.form.get('pagination_tag'),
            'pagination_parameter' : pagination_parameter,
            'thread_post_tag' : request.form.get('thread_post_tag'),
            'thread_post_parameter' : thread_post_parameter,
            'forum_threads_tag' : request.form.get('forum_threads_tag'),
            'forum_threads_parameter' : forum_threads_parameter
        }
        with open("data\\parse_configs.json", 'w', encoding="utf-8") as file:
            file.write(json.dumps(data_to_pass))

        return redirect(url_for('get_other_data'))

    context_ = {
        'mp_amm' : int(mp_amm),
        'pp_amm' : int(pp_amm),
        'tp_amm' : int(tp_amm),
        'ftp_amm' : int(ftp_amm)
    }
    return render_template("tag_data.html", context=context_)

# Page to collect pagination type, bot protection case, etc.
@app.route('/other_data/', methods=["GET", "POST"])
def get_other_data():
    if request.method == "POST":

        data = dict
        with open("data\\parse_configs.json", 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        data['pagination_case'] = request.form.get('paginationCase')
        if data['pagination_case'] == 'C':
            data['thread_step'] = request.form.get('threadStep')
            data['forum_step'] = request.form.get('forumStep')

        data['pagination_template'] = request.form.get('paginationTemplate')

        if request.form.get('botProtection') == 'True':
            data['bot_protection'] = 'True'
        else:
            data['bot_protection'] = 'False'

        data['page_load_delay'] = request.form.get('pageLoadDelay')

        data['forum_link'] = request.form.get('forumLink')

        if request.form.get('loginRequirment') == 'True':
            data['login_requirment'] = 'True'
        else:
            data['login_requirment'] = 'False'

        with open("data\\parse_configs.json", 'w', encoding='utf-8') as file:
            file.write(json.dumps(data))
        
        return redirect(url_for('show_results'))
    return render_template('other_data.html')

# Page for final confirmation of inputed data
@app.route("/results/", methods=['GET'])
def show_results():
    with open("data\\parse_configs.json", 'r', encoding="utf-8") as file:
        data = json.load(file)
        to_pass = {
                'message_tag' : data['message_tag'],
                'message_parameter' : data['message_parameter'],
                'pagination_tag' : data['pagination_tag'],
                'pagination_parameter' : data['pagination_parameter'],
                'thread_post_tag' : data['thread_post_tag'],
                'thread_post_parameter' : data['thread_post_parameter'],
                'forum_threads_tag' : data['forum_threads_tag'],
                'forum_threads_parameter' : data['forum_threads_parameter'],
                'pagination_case' : data['pagination_case'],
                'pagination_template' : data['pagination_template'],
                'page_load_delay' : data['page_load_delay'],
                'forum_link' : data['forum_link'],
                'login_requirment' : data['login_requirment']
        }

        if data['pagination_case'] == 'C':
            to_pass['thread_step'] = data['thread_step']
            to_pass['forum_step'] = data['forum_step']
    
    return render_template("result.html", context=to_pass)

# Logic to save currently inputed data as a new template
@app.route('/save_template')
def save_template():

    with open('data/parse_configs.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        link_ = data['forum_link']
    if ('https://' in link_):
        link_ = link_.replace('https://', '')
    if ('http://' in link_):
        link_ = link_.replace('http://', '')
        
    new_file_name = link_.split('/')[0]

    try:
        with open(f'data/saved_templates/{new_file_name}.json', 'x', encoding='utf-8') as new_file:
            new_file.write(json.dumps(data))
    except FileExistsError:
        print(f"File {new_file_name}.json already exists!")

    return redirect(url_for('index'))

start()