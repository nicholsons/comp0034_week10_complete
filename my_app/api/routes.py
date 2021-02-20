from flask import Blueprint, jsonify, make_response, request
from flask_httpauth import HTTPBasicAuth

from my_app import db
from my_app.models import Profile, User

api_bp = Blueprint('api', __name__, url_prefix='/api')

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(email=username).first()
    if user and user.check_password(password):
        return user


@api_bp.route('/profiles', methods=['GET'])
@auth.login_required()
def get_profiles():
    profiles = Profile.query.all()
    json = jsonify(profiles=[p.serialize for p in profiles])
    return make_response(json, 200)


@api_bp.route('/profiles/<int:userid>', methods=['GET'])
@auth.login_required()
def get_profile(userid):
    profile = Profile.query.filter_by(id=userid).first_or_404()
    json = jsonify(profile=profile.serialize)
    return make_response(json, 200)


@api_bp.route('/profiles', methods=['POST'])
@auth.login_required()
def post_profile():
    """
    Creates a new profile.
    User must be an existing user.
    Username is required and must be unique.
    Area must be in the given list in the area table.
    TODO: Apply validation to the fields
    """
    user_id = request.args.get('userid', type=int)
    bio = request.args.get('bio', type=str)
    area = request.args.get('area', type=str)
    username = request.args.get('username', type=str)
    if username is None:
        headers = {"Content-Type": "application/json"}
        json = jsonify({'message': 'Please provide a username'})
        return make_response(json, 400, headers)
    profile = Profile(user_id=user_id, username=username, bio=bio, area=area)
    db.session.add(profile)
    db.session.commit()
    uri = f'http://127.0.0.1:5000/api/{user_id}'
    json = jsonify({'message': uri})
    headers = {"Content-Type": "application/json"}
    return make_response(json, 201, headers)


@api_bp.route('/users', methods=['POST', 'GET'])
def create_user():
    """
    Creates a new user.
    User table requires email address, password, firstname and lastname.
    Since we only need two fields for the api users I am adding dummy data to the other fields.
    TODO: Check that the username is a valid email address.
    """
    username = request.args.get('username')
    password = request.args.get('password')
    firstname = "None"
    lastname = "None"
    if username is None or password is None:
        json = jsonify({'message': 'Missing username or password'})
        return make_response(json, 400)
    if User.query.filter_by(email=username).first() is not None:
        json = jsonify({'message': 'Duplicate username'})
        return make_response(json, 400)
    user = User(email=username, firstname=firstname, lastname=lastname)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    json = jsonify({'userid': '{}'.format(user.id), 'username': '{}'.format(user.email)})
    return make_response(json, 201)


@api_bp.errorhandler(404)
def not_found():
    error = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    response = jsonify(error)
    return make_response(response, 404)


@api_bp.errorhandler(401)
def not_authorised():
    error = {
        'status': 401,
        'message': 'You must provide username and password to access this resource',
    }
    response = jsonify(error)
    return make_response(response, 401)
