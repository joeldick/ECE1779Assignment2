from app import app

from flask import render_template

@app.route('/old')
# main landing page
def index_old():
    return render_template("index_old.html",
                           page_header="Welcome to ECE1771 Assignment 2")