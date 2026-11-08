from flask import Flask, render_template, redirect, url_for, request, Response, session
from werkzeug.security import check_password_hash
import database
from itertools import zip_longest
import config
from functools import wraps
from datetime import timedelta
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
app.config['SECRET_KEY'] = config.SK
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
#TODO: turn these back on for deployment
#app.config["SESSION_COOKIE_SECURE"] = True
#app.config["DEBUG"] = False

csrf = CSRFProtect(app)

DAYS = [("Monday", "Mon"),
        ("Tuesday", "Tues"),
        ("Wednesday", "Wed"),
        ("Thursday", "Thurs"),
        ("Friday", "Fri")]

def login_required(admin_function):

    @wraps(admin_function)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for('user_login'))

        return admin_function(*args, **kwargs)

    return wrapper

#Main Route is the text string generator for ease of user use
@app.route('/', methods=['GET', 'POST'])
def text_form() -> str | tuple[str,int]:
    """route for text string generator tool"""
    sites = database.get_site_list()
    site_lookup = {
        key: code
        for site_name, code in sites
        for key in (site_name, code)
    }

    if request.method == 'GET':
        return render_template("formPageSite.html", sites=sites)

    step = request.form.get('step')

    if step == 'site':
        data = request.form
        return render_template('formPageDay.html', data=data, days=DAYS)

    elif step == 'day':
        data = request.form
        flat_data = data.to_dict(flat=False)

        site_shortcode = site_lookup[data.get('site')]
        roster = database.get_sked_by_day(flat_data['day'][0], site_shortcode)

        initials = []
        for person in roster:
            initials.append(person[0])

        splitty = [x.split("-", 1)[0] for x in initials]

        return render_template('formPageInitials.html', attendees=splitty, data=data)

    elif step == 'initials':
        data = request.form
        flat_data = data.to_dict(flat=False)

        str_render = f'{' '.join(str(x) for x in flat_data['initials'])} present at {flat_data['site'][0]}'

        return render_template('textgen.html', str_render=str_render)

    else:
        return "Unknown form step", 400

@app.route('/brickhorse', methods=['GET', 'POST'])
def user_login() -> str | Response:
    if request.method == 'GET':
        return render_template("login.html")

    creds = request.form
    if check_password_hash(config.ADMIN_PASSWORD_HASH, creds["password"]) and config.ADMIN_USERNAME == creds["username"]:
        session.clear()
        session.permanent = True
        session["admin_logged_in"] = True
        return redirect(url_for('admin_landing'))
    else:
        return render_template("login.html", error="Incorrect username or password")

@app.route('/brickhorse2', methods=['POST'])
def user_logout() -> str | Response:
    session.clear()
    return redirect(url_for('user_login'))

@app.route('/admin', methods=['GET'])
@login_required
def admin_landing() -> str:
    """main landing page for the admin section"""
    return render_template("admin_landing.html")

@app.route('/admin/sites', methods=['GET', 'POST'])
@login_required
def admin_sites() -> str | tuple[str,int]:
    """lists sites from database, and allows adding or removing sites"""
    sites = database.get_site_list()
    if request.method == 'GET':
        return render_template("admin_list_sites.html", sites=sites)

    operation = request.form.get('operation')

    if operation == 'add':
            return render_template("admin_add_site.html")

    elif operation == 'remove':
        return render_template("admin_remove_site.html", sites=sites)

    else:
        return "Unknown operation", 400

@app.route('/admin/sites/add', methods=['POST'])
@login_required
def admin_add_sites() -> Response:
    """database connection for adding new sites"""
    data = request.form
    flat_data = data.to_dict(flat=False)

    database.add_site(flat_data['code'][0], flat_data['name'][0])
    return redirect(url_for('admin_sites'))

@app.route('/admin/sites/remove', methods=['POST'])
@login_required
def admin_remove_sites() -> Response:
    """database connection for removing closed sites"""
    data = request.form
    flat_data = data.to_dict(flat=False)

    database.remove_site(flat_data['code'][0])

    return redirect(url_for('admin_sites'))

@app.route('/admin/roster', methods=['GET', 'POST'])
@login_required
def admin_roster() -> str | tuple[str,int]:
    """lists initials, and allows for adding or removing initials from database"""
    roster = [x[0] for x in database.get_roster()]

    if request.method == 'GET':
        return render_template("admin_list_initials.html", roster=roster)

    operation = request.form.get('operation')

    if operation == 'add':
            return render_template("admin_add_initials.html")

    elif operation == 'remove':
        return render_template("admin_remove_initials.html", roster=roster)

    else:
        return "Unknown operation", 400

@app.route('/admin/roster/add', methods=['POST'])
@login_required
def admin_add_initials() -> Response:
    """database connection for adding new initials"""
    data = request.form
    flat_data = data.to_dict(flat=False)

    database.add_initials(flat_data['name'][0])
    return redirect(url_for('admin_roster'))

@app.route('/admin/roster/remove', methods=['POST'])
@login_required
def admin_remove_initials() -> Response:
    """database connection for removing initials from roster"""
    data = request.form
    flat_data = data.to_dict(flat=False)

    database.remove_initials(flat_data['name'][0])
    return redirect(url_for('admin_roster'))

@app.route('/admin/schedule', methods=['GET', 'POST'])
@login_required
def admin_sked() -> str:
    """main landing page for selecting site to view current schedule"""

    sites = database.get_site_list()

    return render_template("admin_sked_landing.html", sites=sites)

@app.route('/admin/schedule/<site>', methods=['GET', 'POST'])
@login_required
def admin_site_sked(site: str) -> str:
    """displays schedule roster of chosen site"""
    operation = request.form.get('operation')

    full_roster = database.get_roster()
    cleaned_roster = [x[0] for x in full_roster if x[0] is not None]

    sked = []
    for day in DAYS:
        daily_roster = database.get_sked_by_day(day[1], site)
        sked.append([x[0] for x in daily_roster])

    site_roster =set( [init for daily in sked for init in daily])

    columns = list(zip_longest(*sked, fillvalue=""))

    if operation == 'add':
        return render_template("admin_add_to_sked.html", roster=cleaned_roster, days=DAYS, site=site)

    elif operation == 'remove':
        return render_template("admin_remove_from_sked.html", roster=site_roster, days=DAYS, site=site)

    return render_template("admin_weekly_site_sked.html", days=DAYS, sked=columns, site=site)

@app.route('/admin/schedule/<site>/add', methods=['POST'])
@login_required
def admin_add_sked(site: str) -> str | Response:
    """allows for adding a student to a site on a particular day"""
    data = request.form
    flat_data = data.to_dict(flat=False)

    persons = database.get_roster()
    cleaned_roster = [x[0] for x in persons if x[0] is not None]

    #error handling if there's no day or student selected
    if 'day' not in flat_data:
        error = "Please select a day"
        return render_template("admin_add_to_sked.html", roster=cleaned_roster, site=site, days=DAYS, error=error)
    elif len(flat_data['initials'][0]) == 0:
        error = "Please select a student"
        return render_template("admin_add_to_sked.html", roster=cleaned_roster, site=site, days=DAYS, error=error)

    for day in flat_data['day']:
       database.add_to_sked(site, day, flat_data['initials'][0])

    return redirect(url_for('admin_site_sked', site=site ))

@app.route('/admin/schedule/<site>/remove', methods=['POST'])
@login_required
def admin_remove_sked(site: str) -> str | Response:
    """allows for removing a student from a site on a particular day"""
    data = request.form
    flat_data = data.to_dict(flat=False)

    sked = []
    for day in DAYS:
        daily_roster = database.get_sked_by_day(day[1], site)
        sked.append([x[0] for x in daily_roster])

    site_roster =set( [init for daily in sked for init in daily])

    if 'day' not in flat_data:
        error = "Please select a day"
        return render_template("admin_remove_from_sked.html", roster=site_roster, site=site, days=DAYS, error=error)
    elif len(flat_data['initials'][0]) == 0:
        error = "Please select a student"
        return render_template("admin_remove_from_sked.html", roster=site_roster, site=site, days=DAYS, error=error)

    for day in flat_data['day']:
        database.remove_from_sked(site, day, flat_data['initials'][0])

    return redirect(url_for('admin_site_sked', site=site ))

@app.route('/gzs', methods=['GET', 'POST'])
@login_required
def generate_report():
    """route to generate reports"""
    return "TODO: future feature"