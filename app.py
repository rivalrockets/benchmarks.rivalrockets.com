#!flask/bin/python
import os
from flask import Flask, jsonify, abort, g, url_for, make_response
from flask_httpauth import HTTPBasicAuth
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from models import User, Machine, db


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
auth = HTTPBasicAuth()
api = Api(app)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)


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


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SECRET_KEY'] = 'quincy the kumquat queried the queen'

db.init_app(app)

# flask_restful fields usage:
# note that the 'Url' field type takes the 'endpoint' for the arg
user_fields = {
    'username': fields.String,
    'uri': fields.Url('user', absolute=True)
}

machine_fields = {
    'system_name': fields.String,
    'system_notes': fields.String,
    'owner': fields.String,
    'uri': fields.Url('machine', absolute=True),
    'author_id': fields.Integer
}


# New user API class
class UserAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type = str, required = True, location = 'json')
        self.reqparse.add_argument('password', type = str, required = True, location = 'json')
        super(UserAPI, self).__init__()

    @marshal_with(user_fields, envelope='user')
    def get(self, id):
        return User.query.get_or_404(id)
    
    @marshal_with(user_fields, envelope='user')
    def post(self):
        args = self.reqparse.parse_args()
        user = User(username=args['username'])
        user.hash_password(args['password'])
        db.session.add(user)
        db.session.commit()
        return user, 201


# New Token API class
class TokenAPI(Resource):
    decorators = [auth.login_required]

    def get(self):
        token = g.user.generate_auth_token(600)
        return {'token': token.decode('ascii'), 'duration': 600}


# View subclass of Resource (which inherits from MethodView)
class MachineListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('system_name', type = str, required = True, help = 'No machine name provided', location = 'json')
        self.reqparse.add_argument('system_notes', type = str, default = "", location = 'json')
        self.reqparse.add_argument('owner', type = str, default = "", location = 'json')
        super(MachineListAPI, self).__init__()

    @marshal_with(machine_fields, envelope='machines')
    def get(self): 
        return Machine.query.all()
    
    @auth.login_required
    @marshal_with(machine_fields, envelope='machine')
    def post(self):
        args = self.reqparse.parse_args()
        machine = Machine(system_name=args['system_name'], system_notes=args['system_notes'], owner=args['owner'],
                                            author_id=g.user.id) 

        db.session.add(machine)
        db.session.commit()
        return machine, 201


class MachineAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('system_name', type = str, location = 'json')
        self.reqparse.add_argument('system_notes', type = str, location = 'json')
        self.reqparse.add_argument('owner', type = str, location = 'json')
        super(MachineAPI, self).__init__()

    @marshal_with(machine_fields, envelope='machine')
    def get(self, id):
        return Machine.query.get_or_404(id)

    @auth.login_required
    @marshal_with(machine_fields, envelope='machine')
    def put(self, id):
        machine = Machine.query.get_or_404(id)

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
        return machine
    @auth.login_required
    def delete(self, id):
        Machine.query.filter(Machine.id == id).delete()
        db.session.commit()
        return {'result': True}


api.add_resource(UserAPI, '/api/v1.0/users', endpoint = 'users')
api.add_resource(UserAPI, '/api/v1.0/users/<int:id>', endpoint = 'user')
api.add_resource(TokenAPI, '/api/v1.0/token', endpoint = 'token')
api.add_resource(MachineListAPI, '/api/v1.0/machines', endpoint = 'machines')
api.add_resource(MachineAPI, '/api/v1.0/machines/<int:id>', endpoint = 'machine')


if __name__ == '__main__':
    # http://stackoverflow.com/a/19008403
    with app.app_context():
        db.create_all()
    app.run(debug=True)
