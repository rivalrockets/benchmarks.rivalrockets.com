#!flask/bin/python
from flask import Flask, jsonify, abort, url_for

app = Flask(__name__)


# 3. improved 404 error handler that responds with JSON
from flask import make_response

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# 8. A deceptively simple authentication scheme
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()


@auth.get_password
def get_password(username):
    if username == 'kit':
        return 'password'
    return None


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
machine_fields = {
    'system_name': fields.String,
    'system_notes': fields.String,
    'owner': fields.String,
    'uri': fields.Url('machine')
}


# Now with Flask-RESTful adds Api, Resource, reqparse, fields, and marshal
api = Api(app)

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


api.add_resource(MachineListAPI, '/api/v1.0/machines', endpoint = 'machines')
api.add_resource(MachineAPI, '/api/v1.0/machines/<int:id>', endpoint = 'machine')


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
