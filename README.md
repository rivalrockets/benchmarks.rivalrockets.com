# rivalrockets-api

Benchmark score sharing RESTful API application

Written in Python 3 using Flask, Flask-RESTFul.

## Running locally

First cd to the root of the project and set up your virtual environment (python 3):

    $ python -m venv venv

this will create a folder called `venv` in the root.

Then activate your virtual environment:

    $ source venv/bin/activate

Now install the python packages listed in the requirements.txt with `pip`:

    (venv) $ pip install -r requirements.txt

Next run the exports to tell the `flask` CLI to use the rivalrockets-api.py for the `app` function and also set the environment variable to tell `flask` this is the development environment.

    (venv) $ export FLASK_APP=rivalrockets-api.py
    (venv) $ export FLASK_ENV=development

Then run the following to set up the local dev SQLite database (you only need to do this once).

    (venv) $ flask db upgrade

Now run the following to fire up the Flask app for local dev and testing at http://127.0.0.1:5000/api/v1.0/

    (venv) $ flask run
