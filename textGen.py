
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, redirect, url_for, request
import sqlite3

app = Flask(__name__)

#PA DB location
#db_loc = '/home/jwailes/CC/textgen.db'

#local DB location
db_loc = './textgen.db'

#Main Route is the start of the text string generator for ease of user use
@app.route('/', methods=['GET', 'POST'])
def text_form():
    print("Route reached:", request.method)
    print("Form data:", request.form)
    if request.method == 'GET':
        print("here i am!")
        return render_template("formPageSite.html")

    step = request.form.get('step')

    if step == 'site':

        data = request.form
        return render_template('formPageDay.html', data=data)

    elif step == 'day':
        data = request.form
        flat_data = data.to_dict(flat=False)
        print(flat_data)

        conn = sqlite3.connect(db_loc)
        print("Opened database successfully")

        cursor = conn.execute('''select site_name, name
            from schedule
            join sites
            on schedule.SITE_ID = sites.id
            join initials
            on schedule.INITIALS_ID = initials.id
            where workday=? and sites.code=?;''', (flat_data['day'][0], flat_data['site'][0]))
        initials = []
        for row in cursor:
            initials.append(row[1])

        conn.close()

        return render_template('formPageInitials.html', attendees=initials, data=data)
    elif step == 'initials':
        data = request.form
        flat_data = data.to_dict(flat=False)

        str_render = f'{' '.join(str(x) for x in flat_data['initials'])} present at {flat_data['site'][0]}'

        return render_template('textgen.html', str_render=str_render)
    else:
        return "Unknown form step", 400