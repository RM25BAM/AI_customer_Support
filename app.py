from flask import Flask
from flask_restful import Api
from server.routes import UserResponse

app = Flask(__name__)
app.url_map.strict_slashes = False
api = Api(app)

api.add_resource(UserResponse, "/query")

if __name__ == "__main__":
    app.run(debug=True)
