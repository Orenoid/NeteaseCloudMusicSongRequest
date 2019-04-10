from flask_restful import Api, Resource
from flask_cors import CORS
from flask import request, Blueprint, jsonify
from app.views import search_songs

api_bp = Blueprint('api', __name__)
CORS(api_bp)
api = Api(api_bp)


@api_bp.route('')
def test_service():
    return 'I\'m still alive.'

class Search(Resource):
    def get(self):
        args = request.args.to_dict()
        return search_songs(**args)

api.add_resource(Search, '/search')