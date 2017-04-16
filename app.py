from __future__ import print_function
import os,sys
from flask import Flask, render_template, request, url_for, redirect, Response, current_app, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user,current_user
from werkzeug.security import generate_password_hash,check_password_hash
from flask.ext.principal import Principal, Permission, RoleNeed,UserNeed
from flask.ext.principal import Identity, identity_changed, identity_loaded, AnonymousIdentity

app = Flask(__name__)
app.secret_key = "foobarbazz"
app.debug = True
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['postgresql://postgres@localhost/raPlus']

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost/raPlus'

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
    return render_template('user/dashboard.html')

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
        request.form['position']
        )

    user.set_password(user.password)
    db.session.add(user)
    db.session.commit()
    print(request.form['position'], file=sys.stderr)
    print("Trying to print position", file=sys.stderr)
    return redirect(request.args.get('next') or '/')

# post one on one
@app.route('/submit_1-1', methods=['POST'])
def post_1():
    resident1 = modules.OneonOne(
        request.form['resident_first_name'],
        request.form['resident_last_name'],
        request.form['housing'],
        request.form['room_number'],
        request.form['recommended_resources'],
        request.form['concerns'],
        request.form['notes']
        )
    db.session.add(resident1)
    db.session.commit()
    return redirect(url_for('home'))

# post new program
@app.route('/post_program', methods=['POST'])
def post_program():
    program = modules.Program(
        request.form['program_name'],
        request.form['program_type'],
        request.form['date'],
        request.form['time'],
        request.form['location'],
        request.form['primary_sponsor'],
        request.form['secondary_sponsor'],
        request.form['community'],
        request.form['organizations_involved'],
        request.form['money_spent'],
        request.form['description'],
        request.form['implementation'],
        request.form['improvement'],
        request.form['assessment']
        )
    db.session.add(program)
    db.session.commit()
    return redirect(url_for('home'))

# query programs
@app.route('/programs')
def programs():
    allPrograms = modules.Program.query.all()
    return render_template('user/programs_list.html', allPrograms = allPrograms)

# query OneonOnes
@app.route('/OneonOne')
def OneonOne():
    OneonOneList = modules.Program.query.all()
    return render_template('user/oneonone_list.html', OneonOneList = OneonOneList)

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

@app.route('/hummus')
@login_required
def hummus():
    return "The current user is " + current_user.last_name

@app.route('/test_log')
def test_log():
    x = 'jessehuang@wustl.edu'
    user = modules.User.query.filter_by(email=x).first()
    print(user.first_name, file=sys.stderr)
    login_user(user)
    return user.last_name + " Was logged in"

@app.route('/rcd_only')
@login_required
@rcd_privilege.require()
def rcd_only():
    return "For RCD only"

@app.route('/rcd_or_ra')
@login_required
@ra_privilege.require()
def rcd_or_ra():
    return "Either RCD or RA can access this page"

if __name__ == '__main__':
    app.run()
