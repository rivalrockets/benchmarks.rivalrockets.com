from flask import make_response, jsonify
from . import api_blueprint


@api_blueprint.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@api_blueprint.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)
