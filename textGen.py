# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, redirect, url_for, request
import database

app = Flask(__name__)

#Main Route is the text string generator for ease of user use
@app.route('/', methods=['GET', 'POST'])
def text_form():

    if request.method == 'GET':
        return render_template("formPageSite.html")

    step = request.form.get('step')

    if step == 'site':
        data = request.form
        return render_template('formPageDay.html', data=data)

    elif step == 'day':
        data = request.form
        flat_data = data.to_dict(flat=False)

        roster = database.get_sked_by_day(flat_data['day'][0], flat_data['site'][0])

        initials = []
        for person in roster:
            initials.append(person[0])

        return render_template('formPageInitials.html', attendees=initials, data=data)

    elif step == 'initials':
        data = request.form
        flat_data = data.to_dict(flat=False)

        str_render = f'{' '.join(str(x) for x in flat_data['initials'])} present at {flat_data['site'][0]}'

        return render_template('textgen.html', str_render=str_render)

    else:
        return "Unknown form step", 400