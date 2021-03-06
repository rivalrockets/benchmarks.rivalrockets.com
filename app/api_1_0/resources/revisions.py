from flask import g
from flask_restful import Resource, reqparse, fields, marshal_with
from dateutil import parser
from flask_jwt_extended import jwt_required, get_jwt_identity
from .machines import machine_fields
from ... import db
from ...models import Machine, Revision, User


revision_fields = {
    'id': fields.Integer,
    'cpu_make': fields.String,
    'cpu_name': fields.String,
    'cpu_socket': fields.String,
    'cpu_mhz': fields.Integer(default=None),
    'cpu_proc_cores': fields.Integer(default=None),
    'chipset': fields.String,
    'system_memory_gb': fields.Integer(default=None),
    'system_memory_mhz': fields.Integer(default=None),
    'gpu_name': fields.String,
    'gpu_make': fields.String,
    'gpu_memory_gb': fields.Integer(default=None),
    'revision_notes': fields.String,
    'revision_notes_html': fields.String,
    'pcpartpicker_url': fields.String,
    'timestamp': fields.DateTime(dt_format='iso8601'),
    'machine': fields.Nested(machine_fields),
    'uri': fields.Url('.revision', absolute=True)
}


# global revision list
class RevisionListAPI(Resource):
    @marshal_with(revision_fields, envelope='revisions')
    def get(self):
        return Revision.query.order_by(Revision.timestamp.desc()).all()


class RevisionAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('cpu_make', type=str, location='json')
        self.reqparse.add_argument('cpu_name', type=str, location='json')
        self.reqparse.add_argument('cpu_socket', type=str, location='json')
        self.reqparse.add_argument('cpu_mhz', type=int, location='json')
        self.reqparse.add_argument('cpu_proc_cores', type=int, location='json')
        self.reqparse.add_argument('chipset', type=str, location='json')
        self.reqparse.add_argument('system_memory_gb', type=int,
                                   location='json')
        self.reqparse.add_argument('system_memory_mhz', type=int,
                                   location='json')
        self.reqparse.add_argument('gpu_name', type=str, location='json')
        self.reqparse.add_argument('gpu_make', type=str, location='json')
        self.reqparse.add_argument('gpu_memory_mb', type=int, location='json')
        self.reqparse.add_argument('revision_notes', type=str, location='json')
        self.reqparse.add_argument('pcpartpicker_url', type=str,
                                   location='json')
        self.reqparse.add_argument('timestamp', type=str,
                                   location='json')
        super(RevisionAPI, self).__init__()

    @marshal_with(revision_fields, envelope='revision')
    def get(self, id):
        return Revision.query.get_or_404(id)

    @jwt_required
    @marshal_with(revision_fields, envelope='revision')
    def put(self, id):
        revision = Revision.query.get_or_404(id)
        args = self.reqparse.parse_args()

        for k, v in args.items():
            if v is not None:
                # this code smells of elderberries
                if k == 'timestamp':
                    setattr(revision, k, parser.parse(v))
                else:
                    setattr(revision, k, v)
        db.session.commit()
        return revision

    @jwt_required
    def delete(self, id):
        Revision.query.filter(Revision.id == id).delete()
        db.session.commit()
        return {'result': True}


class MachineRevisionListAPI(Resource):
    def __init__(self):
        self.reqparse=reqparse.RequestParser()
        self.reqparse.add_argument('cpu_make', type=str, location='json')
        self.reqparse.add_argument('cpu_name', type=str, location='json')
        self.reqparse.add_argument('cpu_socket', type=str, location='json')
        self.reqparse.add_argument('cpu_mhz', type=int, location='json')
        self.reqparse.add_argument('cpu_proc_cores', type=int, location='json')
        self.reqparse.add_argument('chipset', type=str, location='json')
        self.reqparse.add_argument('system_memory_gb', type=int,
                                   location='json')
        self.reqparse.add_argument('system_memory_mhz', type=int,
                                   location='json')
        self.reqparse.add_argument('gpu_name', type=str, location='json')
        self.reqparse.add_argument('gpu_make', type=str, location='json')
        self.reqparse.add_argument('gpu_count', type=str, location='json')
        self.reqparse.add_argument('gpu_memory_mb', type=int, location='json')
        self.reqparse.add_argument('revision_notes', type=str, location='json')
        self.reqparse.add_argument('pcpartpicker_url', type=str,
                                   location='json')
        self.reqparse.add_argument('timestamp', type=str,
                                   location='json')
        super(MachineRevisionListAPI, self).__init__()

    @marshal_with(revision_fields, envelope='revisions')
    def get(self, id):
        machine = Machine.query.get_or_404(id)
        return machine.revisions.order_by(Revision.timestamp.desc()).all()

    @jwt_required
    @marshal_with(revision_fields, envelope='revision')
    def post(self, id):
        args = self.reqparse.parse_args()

        # parse the timestamp provided
        try:
            ts = parser.parse(args['timestamp'])
        except TypeError:
            ts = None # none will use the model's default (current time)

        current_username = get_jwt_identity()
        current_user = User.find_by_username(current_username)
        machine = Machine.query.get_or_404(id)

        revision = Revision(
            cpu_make=args['cpu_make'],
            cpu_name=args['cpu_name'],
            cpu_socket=args['cpu_socket'],
            cpu_mhz=args['cpu_mhz'],
            cpu_proc_cores=args['cpu_proc_cores'],
            chipset=args['chipset'],
            system_memory_gb=args['system_memory_gb'],
            system_memory_mhz=args['system_memory_mhz'],
            gpu_name=args['gpu_name'],
            gpu_make=args['gpu_make'],
            gpu_memory_mb=args['gpu_memory_mb'],
            gpu_count=args['gpu_count'],
            revision_notes=args['revision_notes'],
            pcpartpicker_url=args['pcpartpicker_url'],
            timestamp=ts,
            author_id=current_user.id)

        machine.revisions.append(revision)

        # commit once to get the id of the revision
        db.session.commit()
        # set the Machine.active_revision_id to this revision
        machine.active_revision_id = revision.id
        # commit again to save the new active_revision_id
        db.session.commit()

        return revision, 201
