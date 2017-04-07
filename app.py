import os,sys
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__) 
app.debug = True

# PostgreSQL for Heroku
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

@app.route('/')
def home():
    return('yo yo yo')

if __name__ == '__main__': 
	app.run()