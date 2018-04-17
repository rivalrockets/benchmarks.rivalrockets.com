from flask import g
from flask_restful import Resource, reqparse, fields, marshal_with
from .authentication import auth
from ... import db
from ...models import User


# flask_restful fields usage:
# note that the 'Url' field type takes the 'endpoint' for the arg
user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'uri': fields.Url('.user', absolute=True),
    'last_seen': fields.DateTime(dt_format='iso8601')
}


# List of users
class UserListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type=str, required=True,
                                   location='json')
        self.reqparse.add_argument('password', type=str, required=True,
                                   location='json')
        super(UserListAPI, self).__init__()

    @marshal_with(user_fields, envelope='users')
    def get(self):
        return User.query.all()

    @marshal_with(user_fields, envelope='user')
    def post(self):
        args = self.reqparse.parse_args()
        user = User(username=args['username'])
        user.hash_password(args['password'])
        db.session.add(user)
        db.session.commit()
        return user, 201


# New user API class
class UserAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type=str, required=False,
                                   location='json')
        self.reqparse.add_argument('password', type=str, required=True,
                                   location='json')
        super(UserAPI, self).__init__()

    @marshal_with(user_fields, envelope='user')
    def get(self, id):
        return User.query.get_or_404(id)

    @auth.login_required
    @marshal_with(user_fields, envelope='user')
    def put(self, id):
        user = User.query.get_or_404(id)

        # only currently logged in user allowed to change their login or pass
        if g.user.id == id:
            # as seen in other places, loop through supplied args to apply
            # the difference is that we're watching out for the password
            args = self.reqparse.parse_args()
            for k, v in args.items():
                if v is not None:
                    if k != "password":
                        setattr(user, k, v)
                    else:
                        user.hash_password(v)

            db.session.commit()
            return user, 201
        else:
            return user, 403
