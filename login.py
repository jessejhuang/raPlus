#reference: http://stackoverflow.com/questions/15231359/split-python-flask-app-into-multiple-files
# from flask import Blueprint
#
# login_py = Blueprint('login_py', __name__)


# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String(80))
#     last_name = db.Column(db.String(80))
#     email = db.Column(db.String(120), unique=True)
#     password = db.Column(db.String(80))
#
#     def __init__(self, first_name, last_name, email, password):
#         self.first_name = first_name
#         self.last_name = last_name
#         self.email = email
#         self.password = password
#
#
#     def __repr__(self):
#         return '<Name %r>' % self.email
#     def is_authenticated():
#         return True
#     def is_active():
#         return True
#     def is_anonymous():
#         return True
#     def getID():
#         return id




# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     # Here we use a class of some kind to represent and validate our
#     # client-side form data. For example, WTForms is a library that will
#     # handle this for us, and we use a custom LoginForm to validate.
#     form = LoginForm()
#     if form.validate_on_submit():
#         # Login and validate the user.
#         # user should be an instance of your `User` class
#         login_user(user)
#
#         flask.flash('Logged in successfully.')
#
#         next = flask.request.args.get('next')
#         # is_safe_url should check if the url is safe for redirects.
#         # See http://flask.pocoo.org/snippets/62/ for an example.
#         if not is_safe_url(next):
#             return flask.abort(400)
#
#         return flask.redirect(next or flask.url_for('index'))
#     return flask.render_template('login.html', form=form)
