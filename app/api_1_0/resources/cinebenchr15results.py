from flask import g
from flask_restful import Resource, reqparse, fields, marshal_with
from dateutil import parser
from flask_jwt_extended import jwt_required
from .revisions import revision_fields
from ... import db
from ...models import Revision, CinebenchR15Result


cinebenchr15result_fields = {
    'id': fields.Integer,
    'result_date': fields.DateTime(dt_format='iso8601'),
    'cpu_cb': fields.Integer(default=None),
    'opengl_fps': fields.Integer(default=None),
    'revision': fields.Nested(revision_fields),
    'uri': fields.Url('.cinebenchr15result', absolute=True)
}


class CinebenchR15ResultListAPI(Resource):
    @marshal_with(cinebenchr15result_fields,
                  envelope='cinebenchr15results')
    def get(self):
        return CinebenchR15Result.query.order_by(
            CinebenchR15Result.cpu_cb.desc()).all()


class CinebenchR15ResultAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('result_date', type=str, location='json')
        self.reqparse.add_argument('cpu_cb', type=int, location='json')
        self.reqparse.add_argument('opengl_fps', type=int, location='json')
        super(CinebenchR15ResultAPI, self).__init__()

    @marshal_with(cinebenchr15result_fields, envelope='cinebenchr15result')
    def get(self, id):
        return CinebenchR15Result.query.get_or_404(id)

    @jwt_required
    @marshal_with(cinebenchr15result_fields, envelope='cinebenchr15result')
    def put(self, id):
        cinebenchr15result = CinebenchR15Result.query.get_or_404(id)
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v is not None:
                # *sniff* you smell that?
                if k == 'result_date':
                    setattr(cinebenchr15result, k, parser.parse(v))
                else:
                    setattr(cinebenchr15result, k, v)
        db.session.commit()
        return cinebenchr15result

    @jwt_required
    def delete(self, id):
        CinebenchR15Result.query.filter(CinebenchR15Result.id == id).delete()
        db.session.commit()
        return {'result': True}


class RevisionCinebenchR15ResultListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('result_date', type=str, location='json')
        self.reqparse.add_argument('cpu_cb', type=int, location='json')
        self.reqparse.add_argument('opengl_fps', type=int, location='json')
        super(RevisionCinebenchR15ResultListAPI, self).__init__()

    @marshal_with(cinebenchr15result_fields, envelope='cinebenchr15results')
    def get(self, id):
        revision = Revision.query.get_or_404(id)
        return revision.cinebenchr15results.all()

    @jwt_required
    @marshal_with(cinebenchr15result_fields, envelope='cinebenchr15result')
    def post(self, id):
        args = self.reqparse.parse_args()

        # parse the timestamp provided
        rd = None
        if args['result_date'] is not None:
            rd = parser.parse(args['result_date'])

        revision = Revision.query.get_or_404(id)

        cinebenchr15result = CinebenchR15Result(
            result_date=rd,
            cpu_cb=args['cpu_cb'],
            opengl_fps=args['opengl_fps'])

        cinebenchr15result.revision_id = revision.id
        db.session.add(cinebenchr15result)
        db.session.commit()

        return cinebenchr15result, 201
