# based on https://flask.palletsprojects.com/en/2.0.x/quickstart/
from flask import Flask

app = Flask(__name__)

# Normally return html
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# getting something from the url
from markupsafe import escape # this is for protecting the app from attacks

@app.route("/<name>")
def hi(name):
    return f"Hi, {escape(name)}!"

# requests
from flask import request

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return do_the_login()
    else:
        return show_the_login_form()


# template stuff
from flask import render_template

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)



# handelling requests

from flask import request

with app.test_request_context('/posthere', method='POST'):
    # now you can do something with the request until the
    # end of the with block, such as basic assertions:
    assert request.path == '/posthere'
    assert request.method == 'POST'


@app.route('/doubleRequestHandelling', methods=['POST', 'GET'])
def doubleRequestHandelling():
    print(request.environ)
    error = None
    if request.method == 'POST':
        if request.form['username'] == "foo" and request.form['password'] == "bar":
            return "correct"
        else:
            error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return error


# run the ting
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6001)