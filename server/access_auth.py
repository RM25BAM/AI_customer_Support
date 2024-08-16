from flask import Flask, request, jsonify
from flask_restful import Resource
from server.database_setup import database_authentication

app = Flask(__name__)

# Calling the setup dunction
data_auth = database_authentication()[0]
db = data_auth[1]


class Signup(Resource):
    def get(self):
        return jsonify({"Message": "Getting the data"})
    
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        role = "employee"

        if name and email and password and role:
            try:
                user = data_auth[0].create_user_with_email_and_password(email, password)
                user_id = user['localId']
                user_data = {
                    "name": name,
                    "email": email,
                    "password": password,
                    "role": role,
                }
                db.child('users').child(user_id).set(user_data)
                message = f"User signed up and data stored successfully. {user_id}"
                return jsonify({"message": message})
            except Exception as e:
                error_message = f"An error occurred: {e}"
                return jsonify({"message": error_message})
        else:
            error_message = "All fields are required"
            return jsonify({"message":error_message})


class Login(Resource):
    def get(self):
        return jsonify({"Message": "Nope"})
    def post(self):
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        if email and password:
            try:
                user = data_auth[0].sign_in_with_email_and_password(email, password)
                userid = user['localId']
                if user:
                    # Store login data
                    user_data = {"email": email}
                    db.child("login").child(userid).set(user_data)
                    # message = f"Sign In successful!, id: {userid}"
                    return jsonify({"role" : getRole(userid)})
            except Exception as e:
                error_message = f"An error occurred: {e}"
                return jsonify({"message" : error_message})
        else:
            error_message = "All field are required"
            return jsonify({"message" : error_message})