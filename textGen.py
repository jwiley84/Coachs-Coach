
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, redirect, url_for, request
import sqlite3

app = Flask(__name__)

#PA DB location
#db_loc = '/home/jwailes/CC/textgen.db'

#local DB location
db_loc = './textgen.db'

#Main Route is the start of the text string generator for ease of user use
@app.route('/', methods=['GET'])
def text_form():
    return render_template("formPageSite.html")

@app.route('/submit-site', methods=['POST'])
def submit_site():

    data = request.form

    return render_template('formPageDay.html', data=data)

@app.route('/submit-day', methods=['POST'])
def submit_day():
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

@app.route('/submit-initials', methods=['POST'])
def submit_initials():

    data = request.form
    flat_data = data.to_dict(flat=False)

    str_render = f'{' '.join(str(x) for x in flat_data['initials'])} present at {flat_data['site'][0]}'

    return render_template('textgen.html', str_render=str_render)


@app.route('/brickhorse')
def addSked():
    return render_template('formAddSked.html')

@app.route('/brickhorse2', methods=['POST'])
def submit_new_student_and_sked():

    data = request.form
    flat_data = data.to_dict(flat=False)

    conn = sqlite3.connect(db_loc)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO initials (NAME) VALUES (?)", flat_data['initials'])

    cursor.execute("SELECT last_insert_rowid()")

    initials_id = cursor.fetchone()[0]
    sked_data = (flat_data['day'][0], initials_id, flat_data['site'][0])

    cursor.execute("INSERT INTO schedule (WORKDAY, INITIALS_ID, SITE_ID) VALUES (?, ?, ?)", (sked_data))
    #last_sked = cursor.lastrowid

    #print("**************THE LAST ROW ID IS HERE: " + str(last_sked))
    #cursor.execute("SELECT * FROM schedule WHERE id = ?", (last_sked,))
    cursor.execute("SELECT * FROM sites WHERE id = ?", (flat_data['site'][0],))
    site = []
    for row in cursor:
        site.append(row[1])

    testing = f"{flat_data['initials'][0]} added to {site[0]} on {flat_data['day'][0]}"

    conn.commit()
    conn.close()

    return render_template('brickhorse2.html', testing=testing)






