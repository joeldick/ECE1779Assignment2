from app import app

from flask import request, render_template, redirect, url_for, session, g

from app.dynamo import dynamodb

app.secret_key = '\x91b\x8d\xfe\x16\xf5\x15\xd0\xee\xb7ZBe\xe7\x17\xc9Cc\x1cy3\x8f\x86\x84\xc7=\x9c2\x94\xa7YE8\x05'


@app.route('/login', methods=['GET', 'POST'])
# take user to login page or login the user
def login():
    # if user is already logged in (already has a session), go back to index
    if 'username' in session:
        return redirect(url_for('index'))
    else:
        # if method=GET take user to login page
        if request.method == 'GET':
            return render_template('login/login.html',
                                   page_header="Login")
        # if method=POST log the user in
        elif request.method == 'POST':

            table = dynamodb.Table('Users')

            provided_username = request.form.get('username')
            provided_password = request.form.get('password')

            # look up the username in the table and get the username/password pair
            response = table.get_item(
                Key={
                    'username': provided_username
                },
                ProjectionExpression="username, password"
            )

            # if username does not exit, return error message
            if 'Item' not in response:
                return render_template('login/login.html',
                                       page_header="Login",
                                       error_msg="No such username",
                                       username=request.form.get('username'))
            # if username does exist, check that password matches
            else:
                true_password = response['Item']['password']

            # if password matches, create a session for the user
            if provided_password == true_password:
                session['username'] = provided_username
                return redirect(url_for('index'))
            # if password doesn't match, return an error message and reload login page
            else:
                return render_template('login/login.html',
                                       page_header="Login",
                                       error_msg="Wrong password",
                                       username=request.form.get('username'))


@app.route('/logout', methods=['GET'])
# log the user out
def logout():
    if 'username' in session:
        session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
# let the user register for a new username and password
def register():
    # if method=GET take user to login page
    if request.method == 'GET':
        return render_template('login/register.html',
                               page_header="Register")
    # if method=POST create a new username and password row in the users table
    elif request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        table = dynamodb.Table('Users')

        # look for username in 'Users' table
        response = table.get_item(
            Key={
                'username': username
            },
            ProjectionExpression="username, password"
        )

        # check if username already exists
        if 'Item' in response:
            return render_template('login/register.html',
                                   error_msg="Username already exits",
                                   username=request.form.get('username'))

        # if name doesn't already exist, add it
        response = table.put_item(
            Item={
                'username': username,
                'password': password
            }
        )

        return redirect(url_for('login'), code=307)
