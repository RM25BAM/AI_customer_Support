from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from dotenv import load_dotenv
import os
from flask_restful import Resource, Api
from flask import Flask, request, jsonify
from server.database_setup import database_authentication

load_dotenv('server/.env.dev')

OPENROUTER_API_KEY=os.getenv('OPENROUTER_API_KEY')

authentication = database_authentication()[0]
realtime_database = database_authentication()[1]

class api_call(Resource):
    def post(self):
        data = request.get_json()
        query = data.get('query')
        user_name = data.get('name')
        converse_id = data.get("converse")

        metadata = realtime_database.child("user").push({
            "query":query,
            "user_name":user_name,
            "conversation":converse_id
        })

        return jsonify({"message":"Suceess!"})





