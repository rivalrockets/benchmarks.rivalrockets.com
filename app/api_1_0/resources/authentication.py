from flask import g, make_response, jsonify
from flask_restful import Resource, reqparse
from flask_httpauth import HTTPBasicAuth
from flask_jwt_extended import (create_access_token, create_refresh_token,
    jwt_refresh_token_required, get_jwt_identity)
from app.models import User


auth = HTTPBasicAuth()


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)
    # return 403 instead of 401 to prevent browsers from
    # displaying the default auth dialog


@auth.verify_password
def verify_password(username, password):
    # try to authenticate with username/password
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True

class UserLogin(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type=str, required=True,
                                   location='json')
        self.reqparse.add_argument('password', type=str, required=True,
                                   location='json')
        super(UserLogin, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        current_user = User.find_by_username(args['username'])

        if not current_user or not current_user.verify_password(args['password']):
            return make_response(jsonify({'message': 'Wrong credentials'}), 401)
        else:
            access_token = create_access_token(identity=args['username'])
            refresh_token = create_refresh_token(identity=args['username'])
            return {
                'message': 'Logged in as {}'.format(current_user.username),
                'access_token': access_token,
                'refresh_token': refresh_token
                }

class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token}
