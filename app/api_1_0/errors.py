from flask import make_response, jsonify
from . import api_blueprint

# This is likely unnecesary because I'm using
# the catch_all_404s constructor option.
@api_blueprint.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
