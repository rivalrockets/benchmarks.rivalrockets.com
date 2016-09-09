#!flask/bin/python
from flask import Flask, jsonify, abort, g, url_for

app = Flask(__name__)


# 3. improved 404 error handler that responds with JSON
from flask import make_response

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# 8. A deceptively simple authentication scheme
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog
    
@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

# Convert simple dict to SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)


# replacing the authentication model to use a simple token-based approach
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

app.config['SECRET_KEY'] = 'quincy the kumquat queried the queen'

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)
    
    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


class Machine(db.Model):
    __tablename__ = 'machines'
    id = db.Column(db.Integer, primary_key=True)
    system_name = db.Column(db.Text)
    system_notes = db.Column(db.Text)
    system_notes_html = db.Column(db.Text)
    owner = db.Column(db.Text)


from flask_restful import Api, Resource, reqparse, fields, marshal

# flask_restful fields usage:
# note that the 'Url' field type takes the 'endpoint' for the arg
user_fields = {
    'username': fields.String,
    'Location': fields.Url('user')
}

machine_fields = {
    'system_name': fields.String,
    'system_notes': fields.String,
    'owner': fields.String,
    'uri': fields.Url('machine')
}


# Now with Flask-RESTful adds Api, Resource, reqparse, fields, and marshal
api = Api(app)

# New user API class
class UserAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type = str, required = True, location = 'json')
        self.reqparse.add_argument('password', type = str, required = True, location = 'json')
        super(UserAPI, self).__init__()

    def get(self, id):
        user = User.query.get(id)
        if user is None:
            abort(404)
        return {'user': marshal(user, user_fields)}
    
    def post(self):
        args = self.reqparse.parse_args()
        user = User(username=args['username'])
        user.hash_password(args['password'])
        db.session.add(user)
        db.session.commit()
        return {'user': marshal(user, user_fields)}, 201


# New Token API class
class TokenAPI(Resource):
    decorators = [auth.login_required]

    def get(self):
        token = g.user.generate_auth_token(600)
        return {'token': token.decode('ascii'), 'duration': 600}


# View subclass of Resource (which inherits from MethodView)
class MachineListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('system_name', type = str, required = True, help = 'No machine name provided', location = 'json')
        self.reqparse.add_argument('system_notes', type = str, default = "", location = 'json')
        self.reqparse.add_argument('owner', type = str, default = "", location = 'json')
        super(MachineListAPI, self).__init__()

    def get(self):
        machines = Machine.query.all()
        return {'machines': [marshal(machine, machine_fields) for machine in machines]}
    
    def post(self):
        args = self.reqparse.parse_args()
        machine = Machine(system_name=args['system_name'], system_notes=args['system_notes'], owner=args['owner']) 

        db.session.add(machine)
        db.session.commit()
        return {'machine': marshal(machine, machine_fields)}, 201


class MachineAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('system_name', type = str, location = 'json')
        self.reqparse.add_argument('system_notes', type = str, location = 'json')
        self.reqparse.add_argument('owner', type = str, location = 'json')
        super(MachineAPI, self).__init__()

    def get(self, id):
        machine = Machine.query.filter(Machine.id==id).first()
        if machine is None:
            abort(404)
        return {'machine': marshal(machine, machine_fields)}

    # why no post()?
    # looks like it's because the the method views of the *ListAPI class don't get 'id'
    # this uses Flask-RESTful's marshal method
    def put(self, id):
        machine = Machine.query.filter(Machine.id==id).first()
        if machine is None:
            abort(404)

        # a little clever loop to go through all the args passed and 
        # apply them to the newly instantiated Machine object
        # since the SQLAlchemy machine object does not support item
        # assignment, let's use some setattr func
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v != None:
                setattr(machine, k, v)
        # autocommit? This doesn't appear to be necessary---leaving in for now.
        db.session.commit()
        return {'machine': marshal(machine, machine_fields)}
    
    def delete(self, id):
        machine = [machine for machine in machines if machine ['id'] == id]
        if len(machine) == 0:
            abort(404)
        machines.remove(machine[0])
        return {'result': True}


api.add_resource(UserAPI, '/api/v1.0/users', endpoint = 'users')
api.add_resource(UserAPI, '/api/v1.0/users/<int:id>', endpoint = 'user')
api.add_resource(TokenAPI, '/api/v1.0/token', endpoint = 'token')
api.add_resource(MachineListAPI, '/api/v1.0/machines', endpoint = 'machines')
api.add_resource(MachineAPI, '/api/v1.0/machines/<int:id>', endpoint = 'machine')


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
