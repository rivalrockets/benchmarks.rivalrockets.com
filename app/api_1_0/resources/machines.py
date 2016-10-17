from flask import g
from flask_restful import Resource, reqparse, fields, marshal_with
from .authentication import auth
from ... import db
from ...models import Machine


machine_fields = {
    'system_name': fields.String,
    'system_notes': fields.String,
    'owner': fields.String,
    'active_revision_id': fields.Integer(default=None),
    'timestamp': fields.DateTime,
    'uri': fields.Url('.machine', absolute=True),
    'author_id': fields.Integer(default=None)
}


# View subclass of Resource (which inherits from MethodView)
class MachineListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('system_name', type=str, required=True, help='No machine name provided',
                                   location='json')
        self.reqparse.add_argument('system_notes', type=str, default="", location='json')
        self.reqparse.add_argument('owner', type=str, default="", location='json')
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
        self.reqparse.add_argument('system_name', type=str, location='json')
        self.reqparse.add_argument('system_notes', type=str, location='json')
        self.reqparse.add_argument('owner', type=str, location='json')
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
            if v is not None:
                setattr(machine, k, v)
        # autocommit? This doesn't appear to be necessary---leaving in for now.
        db.session.commit()
        return machine

    @auth.login_required
    def delete(self, id):
        Machine.query.filter(Machine.id == id).delete()
        db.session.commit()
        return {'result': True}
