from flask_restful import Api, Resource
from flask_cors import CORS
from flask import request, Blueprint, jsonify
import app.views as views

api_bp = Blueprint('api', __name__)
CORS(api_bp)
api = Api(api_bp)

@api_bp.route('')
def test_service():
    return 'I\'m still alive.'

class Search(Resource):
    def get(self):
        args = request.args.to_dict()
        return views.search_songs(**args)

api.add_resource(Search, '/search')

class Playlist(Resource):
    def post(self):
        return views.append_song(**request.json)

api.add_resource(Playlist, '/playlist')