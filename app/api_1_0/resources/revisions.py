from flask import g
from flask_restful import Resource, reqparse, fields, marshal_with
from .authentication import auth
from ... import db
from ...models import Machine, Revision


revision_fields = {
    'cpu_make': fields.String,
    'cpu_name': fields.String,
    'cpu_socket': fields.String,
    'cpu_mhz': fields.Integer(default=None),
    'cpu_proc_cores': fields.Integer(default=None),
    'chipset': fields.String,
    'system_memory_mb': fields.Integer(default=None),
    'system_memory_mhz': fields.Integer(default=None),
    'gpu_name': fields.String,
    'gpu_make': fields.String,
    'gpu_memory_gb': fields.Integer(default=None),
    'revision_notes': fields.String,
    'revision_notes_html': fields.String,
    'pcpartpicker_url': fields.String,
    'timestamp': fields.DateTime,
    'author_id': fields.Integer(default=None),
    'machine_id': fields.Integer(default=None),
    'uri': fields.Url('.revision', absolute=True)
}


# global revision list... might be better to have a per-machine revision list only.
class RevisionListAPI(Resource):
    @marshal_with(revision_fields, envelope='revisions')
    def get(self):
        return Revision.query.all()


class RevisionAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('cpu_make', type=str, location='json')
        self.reqparse.add_argument('cpu_name', type=str, location='json')
        self.reqparse.add_argument('cpu_socket', type=str, location='json')
        self.reqparse.add_argument('cpu_mhz', type=int, location='json')
        self.reqparse.add_argument('cpu_proc_cores', type=int, location='json')
        self.reqparse.add_argument('chipset', type=str, location='json')
        self.reqparse.add_argument('system_memory_gb', type=int, location='json')
        self.reqparse.add_argument('system_memory_mhz', type=int, location='json')
        self.reqparse.add_argument('gpu_name', type=str, location='json')
        self.reqparse.add_argument('gpu_make', type=str, location='json')
        self.reqparse.add_argument('gpu_memory_mb', type=int, location='json')
        self.reqparse.add_argument('revision_notes', type=str, location='json')
        self.reqparse.add_argument('pcpartpicker_url', type=str, location='json')
        super(RevisionAPI, self).__init__()

    @marshal_with(revision_fields, envelope='revision')
    def get(self, id):
        return Revision.query.get_or_404(id)

    @auth.login_required
    @marshal_with(revision_fields, envelope='revision')
    def put(self, id):
        revision = Revision.query.get_or_404(id)
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v is not None:
                setattr(revision, k, v)
        db.session.commit()
        return revision

    @auth.login_required
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
        self.reqparse.add_argument('system_memory_gb', type=int, location='json')
        self.reqparse.add_argument('system_memory_mhz', type=int, location='json')
        self.reqparse.add_argument('gpu_name', type=str, location='json')
        self.reqparse.add_argument('gpu_make', type=str, location='json')
        self.reqparse.add_argument('gpu_count', type=str, location='json')
        self.reqparse.add_argument('gpu_memory_mb', type=int, location='json')
        self.reqparse.add_argument('revision_notes', type=str, location='json')
        self.reqparse.add_argument('pcpartpicker_url', type=str, location='json')
        super(MachineRevisionListAPI, self).__init__()

    @marshal_with(revision_fields, envelope='revisions')
    def get(self, id):
        machine = Machine.query.get_or_404(id)
        return machine.revisions.all()

    @auth.login_required
    @marshal_with(revision_fields, envelope='revision')
    def post(self, id):
        args = self.reqparse.parse_args()
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
            author_id=g.user.id)

        # Why doesn't this work?
        #revision.machine = machine
        # Instead, I'm doing this:
        revision.machine_id = machine.id

        #TODO: set the Machine.active_revision_id to this revision

        db.session.add(revision)
        db.session.commit()
        return revision, 201