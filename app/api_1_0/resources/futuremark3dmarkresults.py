from flask_restful import Resource, reqparse, fields, marshal_with
from dateutil import parser
from sqlalchemy import desc
from ..resources.authentication import auth
from .revisions import revision_fields
from ... import db
from ...models import Revision, Futuremark3DMarkResult


futuremark3dmarkresult_fields = {
    'id': fields.Integer,
    'result_date': fields.DateTime(dt_format='iso8601'),
    'icestorm_score': fields.Integer(default=None),
    'icestorm_result_url': fields.String,
    'cloudgate_score': fields.Integer(default=None),
    'cloudgate_result_url': fields.String,
    'firestrike_score': fields.Integer(default=None),
    'firestrike_result_url': fields.String,
    'skydiver_score': fields.Integer(default=None),
    'skydiver_result_url': fields.String,
    'overall_result_url': fields.String,
    'revision': fields.Nested(revision_fields),
    'uri': fields.Url('.futuremark3dmarkresult', absolute=True)
}


class Futuremark3DMarkResultListAPI(Resource):
    @marshal_with(futuremark3dmarkresult_fields,
                  envelope='futuremark3dmarkresults')
    def get(self):
        # order by sum of all scores to come up with kinda "aggregate score"
        return Futuremark3DMarkResult.query.order_by(desc(
            Futuremark3DMarkResult.icestorm_score +
            Futuremark3DMarkResult.cloudgate_score +
            Futuremark3DMarkResult.firestrike_score +
            Futuremark3DMarkResult.skydiver_score)).all()


class Futuremark3DMarkResultAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('result_date', type=str,
                                   location='json')
        self.reqparse.add_argument('icestorm_score', type=int,
                                   location='json')
        self.reqparse.add_argument('icestorm_result_url', type=str,
                                   location='json')
        self.reqparse.add_argument('cloudgate_score', type=int,
                                   location='json')
        self.reqparse.add_argument('cloudgate_result_url', type=str,
                                   location='json')
        self.reqparse.add_argument('firestrike_score', type=int,
                                   location='json')
        self.reqparse.add_argument('firestrike_result_url', type=str,
                                   location='json')
        self.reqparse.add_argument('skydiver_score', type=int,
                                   location='json')
        self.reqparse.add_argument('skydiver_result_url', type=str,
                                   location='json')
        self.reqparse.add_argument('overall_result_url', type=str,
                                   location='json')
        super(Futuremark3DMarkResultAPI, self).__init__()

    @marshal_with(futuremark3dmarkresult_fields,
                  envelope='futuremark3dmarkresult')
    def get(self, id):
        return Futuremark3DMarkResult.query.get_or_404(id)

    @auth.login_required
    @marshal_with(futuremark3dmarkresult_fields,
                  envelope='futuremark3dmarkresult')
    def put(self, id):
        futuremark3dmarkresult = Futuremark3DMarkResult.query.get_or_404(id)
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v is not None:
                # ew.
                if k == 'result_date':
                    setattr(futuremark3dmarkresult, k, parser.parse(v))
                else:
                    setattr(futuremark3dmarkresult, k, v)
        db.session.commit()
        return futuremark3dmarkresult

    @auth.login_required
    def delete(self, id):
        Futuremark3DMarkResult.query.filter(
                                    Futuremark3DMarkResult.id == id).delete()
        db.session.commit()
        return {'result': True}


class RevisionFuturemark3DMarkResultListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('result_date', type=str,
                                   location='json')
        self.reqparse.add_argument('icestorm_score', type=int,
                                   location='json')
        self.reqparse.add_argument('icestorm_result_url', type=str,
                                   location='json')
        self.reqparse.add_argument('cloudgate_score', type=int,
                                   location='json')
        self.reqparse.add_argument('cloudgate_result_url', type=str,
                                   location='json')
        self.reqparse.add_argument('firestrike_score', type=int,
                                   location='json')
        self.reqparse.add_argument('firestrike_result_url', type=str,
                                   location='json')
        self.reqparse.add_argument('skydiver_score', type=int,
                                   location='json')
        self.reqparse.add_argument('skydiver_result_url', type=str,
                                   location='json')
        self.reqparse.add_argument('overall_result_url',
                                   type=str, location='json')
        super(RevisionFuturemark3DMarkResultListAPI, self).__init__()

    @marshal_with(futuremark3dmarkresult_fields,
                  envelope='futuremark3dmarkresults')
    def get(self, id):
        revision = Revision.query.get_or_404(id)
        return revision.futuremark3dmarkresults.all()

    @auth.login_required
    @marshal_with(futuremark3dmarkresult_fields,
                  envelope='futuremark3dmarkresult')
    def post(self, id):
        args = self.reqparse.parse_args()

        # parse the datetime provided
        rd = None
        if args['result_date'] is not None:
            rd = parser.parse(args['result_date'])

        revision = Revision.query.get_or_404(id)

        futuremark3dmarkresult = Futuremark3DMarkResult(
            result_date=rd,
            icestorm_score=args['icestorm_score'],
            icestorm_result_url=args['icestorm_result_url'],
            cloudgate_score=args['cloudgate_score'],
            cloudgate_result_url=args['cloudgate_result_url'],
            firestrike_score=args['firestrike_score'],
            firestrike_result_url=args['firestrike_result_url'],
            skydiver_score=args['skydiver_score'],
            skydiver_result_url=args['skydiver_result_url'],
            overall_result_url=args['overall_result_url'])

        futuremark3dmarkresult.revision_id = revision.id
        db.session.add(futuremark3dmarkresult)
        db.session.commit()

        return futuremark3dmarkresult, 201
