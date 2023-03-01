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

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)
# ADD LOGIN, SIGNUP

@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"msg": "User doesn't exist"}), 404
    if email != user.email or password != user.password:
        return jsonify({"msg": "Bad email or password"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token)

@app.route("/home", methods=["GET"])
@jwt_required()
def home():
    response_body = {
        "msg": "Hello, you are logged in",
    }
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route('/user', methods=['GET'])
def get_users():
    users = User.query.all()
    list_users = list(map(lambda user : user.serialize(), users ))
    response_body = {
        "msg": "Hello, this is your GET /users response ",
        "list_people": list_users
    }
    return jsonify(response_body), 200

@app.route('/signup', methods=['POST'])
def signup():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(email=email).first()
    if user is None:
        new_user = User(email=email, password=password, is_active=True )
        db.session.add(new_user)
        db.session.commit()
        response_body = {
            "msg": "User added correctly"
        }
        return jsonify(response_body), 200

    return jsonify({"msg": "User already exists"}), 404


#select * from people where id = user_id
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.filter_by(id=user_id).first()
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
    response_body = {
        "msg": "Hello, from people",
        "list_people": list_people
    }
    return jsonify(response_body), 200

#select * from people where id = people_id
@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.filter_by(id=people_id).first()
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
    response_body = {
        "msg": "Hello, from planets",
        "list_people": list_planets
    }
    return jsonify(response_body), 200


#select * from people where id = planets_id
@app.route('/planets/<int:planets_id>', methods=['GET'])
def get_planet(planets_id):
    planet = Planets.query.filter_by(id=planets_id).first()
    response_body = {
        "msg": "Hello, from planet",
        "person": planet.serialize()
    }
    return jsonify(response_body), 200


# @app.route('/user/<int:user_id>/favorites',methods=['GET'])
# def get_user_favorites(user_id):
#     user_favorites = Favorites.query.filter_by(user_id=user_id).all() # all() ???
#     list_of_user_favorite = list(map(lambda favorites: favorites.serialize(), user_favorites))

#     if user_favorites is None:
#         response_body = {"Message": "No users favorites to show!"}
#         return jsonify(response_body), 404
#     return jsonify(list_of_user_favorite), 200

@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    favorites_query = Favorites.query.filter_by(user_id=user_id).all()
    list_favorites = []
    print(len(favorites_query))
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

@app.route('/favorites/planets/<int:planets_id>', methods=['POST'])
@jwt_required()
def add_new_favorite_planet(planets_id):
    current_user = get_jwt_identity()
    planets_id = request.json.get("planets_id", None)
    favorites_query = Favorites.query.filter(Favorites.user_id==current_user, Favorites.planets_id==planets_id).first()

    if not favorites_query:
        new_favorite = Favorites(user_id=current_user, planets_id=planets_id)
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({"msg": "Creating favorite"}), 200
    
    return jsonify({"msg": "Favorite already added"}), 401


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
@jwt_required()
def add_new_favorite_people(people_id):
    current_user = get_jwt_identity()
    favorites_query = Favorites.query.filter(Favorites.user_id==current_user, Favorites.people_id==people_id).first()

    if not favorites_query:
        new_favorite = Favorites(user_id=current_user, people_id=people_id)
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({"msg": "Creating favorite"}), 200
    if favorites_query:
        return jsonify({"msg": "Favorite already added"}), 200

    return jsonify({"msg": "Can't add new favorite"}), 401


@app.route('/favorite/planets/<int:planets_id>', methods=['DELETE'])
@jwt_required()
def delete_favorite_planet(planets_id):
    current_user = get_jwt_identity()
    planets_id = request.json.get("planets_id", None)
    favorites_query = Favorites.query.filter(Favorites.user_id==current_user, Favorites.planets_id==planets_id).first()

    if favorites_query:
        favorite = Favorites(user_id=current_user, planets_id=planets_id)
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"msg": "Deleting favorite planet"}), 200
    
    if not favorites_query:
        favorite = Favorites(user_id=current_user, planets_id=planets_id)
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"msg": "Favorite already deleted"}), 200
    
    return jsonify({"msg": "Can't find favorite"}), 401
    

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
@jwt_required()
def delete_favorite_people(people_id):
    current_user = get_jwt_identity()
    favorites_query = Favorites.query.filter(Favorites.user_id==current_user, Favorites.people_id==people_id).all()

    if favorites_query:
        favorite = Favorites(user_id=current_user, people_id=people_id)
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"msg": "Deleting favorite people"}), 200
    
    if not favorites_query:
        return jsonify({"msg": "Favorite already deleted"}), 200
    
    return jsonify({"msg": "Can't find favorite"}), 401


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
