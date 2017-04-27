from __future__ import print_function
import os,sys
from flask import Flask, render_template, request, url_for, redirect, Response, current_app, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user,current_user
from werkzeug.security import generate_password_hash,check_password_hash
from flask_principal import Principal, Permission, RoleNeed,UserNeed
from flask_principal import Identity, identity_changed, identity_loaded, AnonymousIdentity

app = Flask(__name__)
app.secret_key = "foobarbazz"
app.debug = True

#Line below supresses this warning upon python app.py: 'SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and will be disabled by default in the future.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['postgresql://postgres@localhost/raPlus']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost/raPlus'

#import modules after init app
db = SQLAlchemy(app)
import modules

Principal(app)
ra_privilege = Permission(RoleNeed('ra'))
rcd_privilege = Permission(RoleNeed('rcd'))
@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user
    # Add the UserNeed to the identity
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))
    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    if current_user.is_authenticated:
        if current_user.position == 'ra':
            identity.provides.add(RoleNeed('ra'))
            print("Current user is an RA", file=sys.stderr)
        elif current_user.position == 'rcd':
            identity.provides.add(RoleNeed('ra'))
            identity.provides.add(RoleNeed('rcd'))
            print("Current user is an RCD", file=sys.stderr)
        else:
            print("Current user neither RA nor RCD", file=sys.stderr)


@app.route('/')
def login():
    return render_template('main/login.html')

@app.route('/home')
def redirect_to_login():
    return redirect(request.args.get('next') or '/')


@app.route('/dashboard')
@login_required
def dashboard():
    your_programs = modules.Program.query.filter(modules.Program.owner_first_name == current_user.first_name, modules.Program.owner_last_name == current_user.last_name )
    recent_programs = modules.Program.query.order_by(modules.Program.date.desc() ).limit(5).all()
    return render_template('user/dashboard.html', your_programs = your_programs, recent_programs = recent_programs)

@app.route('/features')
def features():
    return render_template('main/features.html')

@app.route('/signup')
def signup():
    return render_template('main/signup.html')

# @app.route('/login')
# def login():
#     return render_template('main/login.html')

@app.route('/submit_program')
def submit():
    return render_template('user/submit_program.html')

@app.route('/submit_1-1')
def submit1():
    return render_template('user/submit_1-1.html')

@app.route('/submit_reminder')
def submit2():
    return render_template('user/submit_reminder.html')

@app.route('/calendar')
def calendar():
    return render_template('user/calendar.html')


# modules below
# post new user
@app.route('/new_user', methods=['POST'])
def new_user():
    user = modules.User(
        request.form['first_name'],
        request.form['last_name'],
        request.form['email'],
        request.form['password'],
        request.form['position'],
        request.form['floor'],
        request.form['residential_college']
        )

    user.set_password(user.password)
    db.session.add(user)
    db.session.commit()
    return redirect(request.args.get('next') or '/')

# post one on one
@app.route('/submit_1-1', methods=['POST'])
def post_1():
    resident1 = modules.one_on_one(
        request.form['resident_first_name'],
        request.form['resident_last_name'],
        request.form['room_number'],
        request.form['date'],
        request.form['notes'],
        current_user.floor,
        current_user.res_college
        )
    db.session.add(resident1)
    db.session.commit()
    return redirect(url_for('dashboard'))

# post new program
@app.route('/post_program', methods=['POST'])
def post_program():
    program = modules.Program(
        request.form['program_name'],
        request.form['program_type'],
        request.form['date'],
        request.form['time'],
        request.form['location'],
        request.form['description'],
        current_user.first_name,
        current_user.last_name,
        request.form['organizations_involved'],
        request.form['community'],
        request.form['money_spent'],
        request.form['implementation'],
        request.form['improvement'],
        request.form['assessment']
        )
    db.session.add(program)
    db.session.commit()
    return redirect(url_for('dashboard'))

# query programs using search bar
@app.route('/programs/q=<search>', methods=['GET', 'POST'])
def programs(search):
    allPrograms = modules.Program.query.filter(modules.Program.program_name.contains(search))
    return render_template('user/programs_list.html', allPrograms = allPrograms)

@app.route('/one_on_one/q=<search>', methods = ['GET', 'POST'])
def one_on_one(search):
    if(current_user.position=='ra'):
        OneonOneList = modules.one_on_one.query.filter(modules.one_on_one.resident_last_name.contains(search), modules.one_on_one.res_college == current_user.res_college, modules.one_on_one.floor == current_user.floor )
        #OneonOneList.append(modules.one_on_one.query.filter(modules.one_on_one.resident_first_name.contains(search), modules.one_on_one.res_college == current_user.res_college, modules.one_on_one.floor == current_user.floor )  )
    else:
        OneonOneList = modules.one_on_one.query.filter(modules.one_on_one.resident_last_name.contains(search), modules.one_on_one.res_college == current_user.res_college)
        #OneonOneList.append(modules.one_on_one.query.filter(modules.one_on_one.resident_first_name.contains(search), modules.one_on_one.res_college == current_user.res_college )  )

    return render_template('user/oneonone_list.html', OneonOneList = OneonOneList)

# query programs
@app.route('/programs')
def all_program():
    allPrograms = modules.Program.query.all()
    return render_template('user/programs_list.html', allPrograms = allPrograms)



# query OneonOnes
@app.route('/OneonOne')
def OneonOne():
    if(current_user.position=='ra'):
        OneonOneList = modules.one_on_one.query.filter(modules.one_on_one.res_college == current_user.res_college, modules.one_on_one.floor == current_user.floor )
    else:
        OneonOneList = modules.one_on_one.query.filter(modules.one_on_one.res_college == current_user.res_college)

    return render_template('user/oneonone_list.html', OneonOneList = OneonOneList)

# query ra using search bar
@app.route('/ra-directory/q=<search>', methods=['GET', 'POST'])
def ra_directory_search(search):
    allRA = modules.ra_directory.query.filter(modules.ra_directory.staff_first_name.contains(search))
    return render_template('user/ra_directory.html', allRA = allRA)

# query ra directory
@app.route('/ra-directory')
def ra_directory():
    allRA = modules.ra_directory.query.all()
    return render_template('user/ra_directory.html', allRA = allRA)


@app.route('/post_login', methods=['POST'])
def post_login():
    form_email = request.form['email']
    form_pass = request.form['password']
    user = modules.User.query.filter_by(email=form_email).first()
    if user is None:
        print("No user with this email")
    elif user.check_password(form_pass):
        print(user.first_name + ' Logged in successfully.',file=sys.stderr)
        login_user(user)
        identity_changed.send(current_app._get_current_object(),identity=Identity(user.id))
        return redirect(url_for('dashboard'))
    else:
        print("Invalid password")
    #return redirect(url_for('home'))
    return render_template('main/login.html')

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return modules.User.query.get(int(user_id))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    # Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    print("You have been logged out ", file=sys.stderr)
    return redirect(request.args.get('next') or '/')

@app.route('/rcd_only')
@login_required
@rcd_privilege.require(http_exception=403)
def rcd_only():
    return "For RCD only"

@app.route('/rcd_or_ra')
@login_required
@ra_privilege.require(http_exception=403)
def rcd_or_ra():
    return "Either RCD or RA can access this page"

@app.errorhandler(403)
def page_not_found(e):
    return render_template('user/403.html'), 403

if __name__ == '__main__':
    app.run()
