"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Favorites
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['POST'])
def create_user():
    user = User()
    body = request.get_json()
    user.email = body['email']
    user.password = body['password']
    user.is_active = body['is_active']
    db.session.add(user)
    db.session.commit()
    return jsonify(user.email)


@app.route('/user', methods=['GET'])
def get_users():

    users =User.query.all()
    all_users = list(map(lambda x: x.serialize(), users))
    return jsonify(all_users), 200


@app.route('/user/favorites', methods=['GET'])
def get_favorites():

    favorites =favorites.query.all()
    all_favorites = list(map(lambda x: x.serialize(), favorites))
    return jsonify(all_favorites), 200

@app.route('/favorites/planets/<int:planet_id>', methods=['POST'])
def create_favorites_planet(planet_id):

    favorites_planet =Favorites(USER_ID = request.get_json()['user_id'],FAV_PLANET_ID = planet_id )
    db.session.add(favorites_planet)
    db.session.commit()
    return jsonify('Planet has been added to favorites!'), 201

@app.route('/favorites/character/<int:character_id>', methods=['POST'])
def create_favorites_character(character_id):

    favorites_character =Favorites(USER_ID = request.get_json()['user_id'],FAV_CHARACTER_ID = character_id )
    db.session.add(favorites_character)
    db.session.commit()
    return jsonify('Character has been added to favorites!'), 201

@app.route('/user/<int:user_id>/favorites/planets/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(user_id, planet_id):

    favorites_user_planet =Favorites.query.filter_by(USER_ID = user_id, FAV_PLANET_ID = planet_id).first()
    if favorites_user_planet is None:
        return jsonify('Could not fine user planet')
    db.session.delete(favorites_user_planet)
    db.session.commit()
    return jsonify('Successfully Deleted'), 200

@app.route('/user/<int:user_id>/favorites/characters/<int:character_id>', methods=['DELETE'])
def delete_favorite_character(user_id, character_id):

    favorites_user_character =Favorites.query.filter_by(USER_ID = user_id, FAV_CHARACTER_ID = character_id).first()
    if favorites_user_character is None:
        return jsonify('Could not fine user character')
    db.session.delete(favorites_user_character)
    db.session.commit()
    return jsonify('Successfully Deleted'), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)