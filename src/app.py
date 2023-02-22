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
from models import db, User, People, Planets, Favorites
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

@app.route('/user', methods=['GET'])
def get_users():
    users = User.query.all()
    list_users = list(map(lambda user : user.serialize(), users ))
    print(list_users)
    response_body = {
        "msg": "Hello, this is your GET /users response ",
        "list_people": list_users
    }
    return jsonify(response_body), 200


#select * from people where id = user_id
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    print(user.serialize())
    response_body = {
        "msg": "Hello, from user",
        "person": user.serialize()
    }
    return jsonify(response_body), 200


@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    #[<People 'Yoda'>, <People 'Darth Vader'>]
    list_people = list(map(lambda person : person.serialize(), people ))
    print(list_people)
    response_body = {
        "msg": "Hello, from people",
        "list_people": list_people
    }
    return jsonify(response_body), 200

#select * from people where id = people_id
@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.filter_by(id=people_id).first()
    print(person.serialize())
    response_body = {
        "msg": "Hello, from person",
        "person": person.serialize()
    }
    return jsonify(response_body), 200


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planets.query.all()
    #[<People 'Planet1'>, <People 'Planet2'>]
    list_planets = list(map(lambda planet : planet.serialize(), planets ))
    print(list_planets)
    response_body = {
        "msg": "Hello, from planets",
        "list_people": list_planets
    }
    return jsonify(response_body), 200


#select * from people where id = planets_id
@app.route('/planets/<int:planets_id>', methods=['GET'])
def get_planet(planets_id):
    planet = Planets.query.filter_by(id=planets_id).first()
    print(planet.serialize())
    response_body = {
        "msg": "Hello, from planet",
        "person": planet.serialize()
    }
    return jsonify(response_body), 200


@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    favorites_query = Favorites.query.filter_by(user_id=user_id)
    list_favorites = []
    for i in favorites_query:
        if i.planets_id == None:
            favorite_people = People.query.filter_by(id=i.people_id).first()
            list_favorites.append(favorite_people.name)
        else:
            favorite_planets = Planets.query.filter_by(id=i.planets_id).first()
            list_favorites.append(favorite_planets.name)

    for i in favorites_query:
        if i.people_id == None:
            favorite_planets = Planets.query.filter_by(id=i.planets_id).first()
            list_favorites.append(favorite_planets.name)
        else:
            favorite_people = People.query.filter_by(id=i.people_id).first()
            list_favorites.append(favorite_people.name)

    response_body = {
        "msg": "Hello, from /user/favorites",
        "list_favorites_{}".format(user_id): list_favorites
    }
    return jsonify(response_body), 200


# @app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
# def add_new_favorite_planet(planet_id):
#     Favorites.append(request.json)
#     return jsonify(Favorites[planet_id]), 200

# @app.route('/favorite/planet/<int:people_id>', methods=['POST'])
# def add_favorite_people(people_id):
#     Favorites.append(request.json)
#     return jsonify(Favorites[people_id]), 200


# @app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
# def delete_favorite_planet(planet_id):
#     Favorites.pop((planet_id-1))
#     return jsonify(Favorites)

# @app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
# def delete_favorite_people(people_id):
#     Favorites.pop((people_id-1))
#     return jsonify(Favorites)



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
