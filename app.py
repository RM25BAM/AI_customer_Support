from flask import Flask
from flask_restful import Api
from server.routes import api_call

app = Flask(__name__)
api = Api(app)
api.add_resource(api_call, "/query")

if __name__ == "__main__":
    app.run(debug=True)
