from flask import Flask, request, render_template, redirect, url_for
import json

app = Flask(__name__)
app.jinja_env.globals['static'] = (
    lambda filename : url_for('static', filename=filename)
)

def start():
    app.run(host='0.0.0.0')

@app.route('/', methods=['GET', 'POST'])
def get_first_data():
    if request.method == 'POST':
        message_parameter_ammount = request.form.get('message_parameter_ammount')
        pagination_parameter_ammount = request.form.get('pagination_parameter_ammount')
        thread_post_parameter_ammount = request.form.get('thread_post_parameter_ammount')
        forum_threads_parameter_ammount = request.form.get('forum_threads_parameter_ammount')
        return redirect(url_for('get_tag_definition', mp_amm = message_parameter_ammount,
                                                    pp_amm = pagination_parameter_ammount,
                                                    tp_amm = thread_post_parameter_ammount,
                                                    ftp_amm = forum_threads_parameter_ammount ))
    return render_template("tag_parameter_ammount.html")


@app.route('/tag_definition/<mp_amm>/<pp_amm>/<tp_amm>/<ftp_amm>', methods=["GET", "POST"])
def get_tag_definition(mp_amm, pp_amm, tp_amm, ftp_amm):
    if request.method == 'POST':
        regex_pattern = '/~/'
        message_parameter = {}
        if mp_amm == '1':
            if request.form.get(f'message_parameter{0}_regex') == 'True':
                message_parameter[request.form.get(f'message_parameter{0}_name')] = regex_pattern + request.form.get(f'message_parameter{0}_value')
            else:
                message_parameter[request.form.get(f'message_parameter{0}_name')] = request.form.get(f'message_parameter{0}_value')
        else:
            for i in range(int(mp_amm)):    
                if request.form.get(f'message_parameter{i}_regex') == 'True':
                    message_parameter[request.form.get(f'message_parameter{i}_name')] = regex_pattern + request.form.get(f'message_parameter{i}_value')
                else:
                    message_parameter[request.form.get(f'message_parameter{i}_name')] = request.form.get(f'message_parameter{i}_value')
        pagination_parameter = {}
        if pp_amm == '1':
            if request.form.get(f'pagination_parameter{0}_regex') == 'True':
                pagination_parameter[request.form.get(f'pagination_parameter{0}_name')] = regex_pattern + request.form.get(f'pagination_parameter{0}_value')
            else:
                pagination_parameter[request.form.get(f'pagination_parameter{0}_name')] = request.form.get(f'pagination_parameter{0}_value')
        else:
            for i in range(int(pp_amm)):
                if request.form.get(f'pagination_parameter{i}_regex') == 'True':
                    pagination_parameter[request.form.get(f'pagination_parameter{i}_name')] = regex_pattern + request.form.get(f'pagination_parameter{i}_value')
                else:
                    pagination_parameter[request.form.get(f'pagination_parameter{i}_name')] = request.form.get(f'pagination_parameter{i}_value')
        thread_post_parameter = {}
        if tp_amm == '1':
            if request.form.get(f'thread_post_parameter{0}_regex') == 'True':
                thread_post_parameter[request.form.get(f'thread_post_parameter{0}_name')] = regex_pattern + request.form.get(f'thread_post_parameter{0}_value')
            else:
                thread_post_parameter[request.form.get(f'thread_post_parameter{0}_name')] = request.form.get(f'thread_post_parameter{0}_value')
        else:
            for i in range(int(tp_amm)):
                if request.form.get(f'thread_post_parameter{i}_regex') == 'True':
                    thread_post_parameter[request.form.get(f'thread_post_parameter{i}_name')] = regex_pattern + request.form.get(f'thread_post_parameter{i}_value')
                else:
                    thread_post_parameter[request.form.get(f'thread_post_parameter{i}_name')] = request.form.get(f'thread_post_parameter{i}_value')
        forum_threads_parameter = {}
        if ftp_amm == '1':
            if request.form.get(f'forum_threads_parameter{0}_regex') == 'True':
                forum_threads_parameter[request.form.get(f'forum_threads_parameter{0}_name')] = regex_pattern + request.form.get(f'forum_threads_parameter{0}_value')
            else:
                forum_threads_parameter[request.form.get(f'forum_threads_parameter{0}_name')] = request.form.get(f'forum_threads_parameter{0}_value')
        else:
            for i in range(int(ftp_amm)):
                if request.form.get(f'forum_threads_parameter{i}_regex') == 'True':
                    forum_threads_parameter[request.form.get(f'forum_threads_parameter{i}_name')] = regex_pattern + request.form.get(f'forum_threads_parameter{i}_value')
                else:
                    forum_threads_parameter[request.form.get(f'forum_threads_parameter{i}_name')] = request.form.get(f'forum_threads_parameter{i}_value')
        
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
        with open("data\\other_soft_tags.txt", 'w', encoding="utf-8") as file:
            file.write(json.dumps(data_to_pass))

    context_ = {
        'mp_amm' : int(mp_amm),
        'pp_amm' : int(pp_amm),
        'tp_amm' : int(tp_amm),
        'ftp_amm' : int(ftp_amm)
    }
    return render_template("needed_data.html", context=context_)

start()