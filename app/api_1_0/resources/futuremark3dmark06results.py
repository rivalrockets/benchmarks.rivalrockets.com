from flask_restful import Resource, reqparse, fields, marshal_with
from dateutil import parser
from flask_jwt_extended import jwt_required
from .revisions import revision_fields
from ... import db


futuremark3dmark06result_fields = {
    'id': fields.Integer,
    'result_date': fields.DateTime(dt_format='iso8601'),
    'sm2_score': fields.Integer(default=None),
    'cpu_score': fields.Integer(default=None),
    'sm3_score': fields.Integer(default=None),
    'proxcyon_fps': fields.Fixed(decimals=2, default=None),
    'fireflyforest_fps': fields.Fixed(decimals=2, default=None),
    'cpu1_fps': fields.Fixed(decimals=2, default=None),
    'cpu2_fps': fields.Fixed(decimals=2, default=None),
    'canyonflight_fps': fields.Fixed(decimals=2, default=None),
    'deepfreeze_fps': fields.Fixed(decimals=2, default=None),
    'overall_score': fields.Integer(default=None),
    'result_url': fields.String(default=None),
    'revision': fields.Nested(revision_fields),
    'uri': fields.Url('.futuremark3dmark06result', absolute=True)
}


from ...models import Revision, Futuremark3DMark06Result

class Futuremark3DMark06ResultListAPI(Resource):
    @marshal_with(futuremark3dmark06result_fields,
                  envelope='futuremark3dmark06results')
    def get(self):
        return Futuremark3DMark06Result.query.order_by(
            Futuremark3DMark06Result.overall_score.desc()).all()


class Futuremark3DMark06ResultAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('result_date', type=str, location='json')
        self.reqparse.add_argument('sm2_score', type=int, location='json')
        self.reqparse.add_argument('cpu_score', type=str, location='json')
        self.reqparse.add_argument('sm3_score', type=int, location='json')
        self.reqparse.add_argument('proxcyon_fps', type=str, location='json')
        self.reqparse.add_argument('fireflyforest_fps', type=int,
                                   location='json')
        self.reqparse.add_argument('cpu1_fps', type=str, location='json')
        self.reqparse.add_argument('cpu2_fps', type=int, location='json')
        self.reqparse.add_argument('canyonflight_fps', type=str,
                                   location='json')
        self.reqparse.add_argument('deepfreeze_fps', type=str, location='json')
        self.reqparse.add_argument('overall_score', type=str, location='json')
        self.reqparse.add_argument('result_url', type=str, location='json')
        super(Futuremark3DMark06ResultAPI, self).__init__()

    @marshal_with(futuremark3dmark06result_fields,
                  envelope='futuremark3dmark06result')
    def get(self, id):
        return Futuremark3DMark06Result.query.get_or_404(id)

    @jwt_required
    @marshal_with(futuremark3dmark06result_fields,
                  envelope='futuremark3dmark06result')
    def put(self, id):
        futuremark3dmark06result = Futuremark3DMark06Result.query.get_or_404(
            id)
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v is not None:
                # *dies a little inside*
                if k == 'result_date':
                    setattr(futuremark3dmark06result, k, parser.parse(v))
                else:
                    setattr(futuremark3dmark06result, k, v)
        db.session.commit()
        return futuremark3dmark06result

    @jwt_required
    def delete(self, id):
        Futuremark3DMark06Result.query\
            .filter(Futuremark3DMark06Result.id == id).delete()
        db.session.commit()
        return {'result': True}


class RevisionFuturemark3DMark06ResultListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('result_date', type=str, location='json')
        self.reqparse.add_argument('sm2_score', type=int, location='json')
        self.reqparse.add_argument('cpu_score', type=str, location='json')
        self.reqparse.add_argument('sm3_score', type=int, location='json')
        self.reqparse.add_argument('proxcyon_fps', type=str, location='json')
        self.reqparse.add_argument('fireflyforest_fps', type=int,
                                   location='json')
        self.reqparse.add_argument('cpu1_fps', type=str, location='json')
        self.reqparse.add_argument('cpu2_fps', type=int, location='json')
        self.reqparse.add_argument('canyonflight_fps', type=str,
                                   location='json')
        self.reqparse.add_argument('deepfreeze_fps', type=str, location='json')
        self.reqparse.add_argument('overall_score', type=str, location='json')
        self.reqparse.add_argument('result_url', type=str, location='json')
        super(RevisionFuturemark3DMark06ResultListAPI, self).__init__()

    @marshal_with(futuremark3dmark06result_fields,
                  envelope='futuremark3dmark06results')
    def get(self, id):
        revision = Revision.query.get_or_404(id)
        return revision.futuremark3dmark06results.all()

    @jwt_required
    @marshal_with(futuremark3dmark06result_fields,
                  envelope='futuremark3dmark06result')
    def post(self, id):
        args = self.reqparse.parse_args()

        # parse the datetime provided
        rd = None
        if args['result_date'] is not None:
            rd = parser.parse(args['result_date'])

        revision = Revision.query.get_or_404(id)

        futuremark3dmark06result = Futuremark3DMark06Result(
            result_date=rd,
            sm2_score=args['sm2_score'],
            cpu_score=args['cpu_score'],
            sm3_score=args['sm3_score'],
            proxcyon_fps=args['proxcyon_fps'],
            fireflyforest_fps=args['fireflyforest_fps'],
            cpu1_fps=args['cpu1_fps'],
            cpu2_fps=args['cpu2_fps'],
            canyonflight_fps=args['canyonflight_fps'],
            deepfreeze_fps=args['deepfreeze_fps'],
            overall_score=args['overall_score'],
            result_url=args['result_url'])

        futuremark3dmark06result.revision_id = revision.id
        db.session.add(futuremark3dmark06result)
        db.session.commit()

        return futuremark3dmark06result, 201
