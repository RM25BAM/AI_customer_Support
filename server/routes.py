from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from dotenv import load_dotenv
import os
from flask_restful import Resource, Api
from flask import Flask, request, jsonify
from server.database_setup import database_authentication
from datetime import datetime
from server.generate_structure_data import google_search
from langchain_ollama import OllamaLLM
from server.ai_setup import configureOllama


load_dotenv('server/.env.dev')



auth, realtime_database, storage = database_authentication()

load_dotenv("server/.env.dev")

my_cse_id = "f188e2180323e449e"
dev_key = os.getenv("GOOGLE_SEARCH_API_KEY")

def format_data(data):
    formattted_data = []
    for _, item in data.items():
        title, link, snippet, paragraph = item
        formattted_data.append(
            f"Title: {title}, Link: {link}, Snippet: {snippet}, Paragraph: {paragraph}"
        )
    return '\n\n'.join(formattted_data)


# Summerizer
def filtered_summarizer(query, paragraph):
    
    model = OllamaLLM(model="llama3.1")
    
    response_schema = [
        ResponseSchema(name="summary", description="A summary of the paragraph."),
        ResponseSchema(name="related", description="Summerize relevant to related to the user's input.")
    ]
    
    output_parser = StructuredOutputParser.from_response_schemas(response_schema)
    format_instructions = output_parser.get_format_instructions()
    
    prompt = PromptTemplate(
        template=(
            "Summarize the following paragraphs into one cohesive summary.\n"
            "{format_instructions}\n\n"
            "{query}"
        ),
        input_variables=["query", "summary"],
        partial_variables={"format_instructions": format_instructions},
    )
    
    chain = prompt | model | output_parser
    result = chain.invoke({"query": query, "summary": paragraph})
    
    return result # response['summary'], response['related']


# API_CALL to get response
# class UserResponse(Resource):
#     def post(self):
#         data = request.get_json()
#         # user_id = data.get('user_id')
#         query = data.get("query")
        
#         search_query = configureOllama(query) # Getting Input Query
#         do_google_search = google_search(search_query, my_cse_id, num=5, cr="us", lr="lang_en") # DO input based on LLM given
#         format_string = format_data(do_google_search) # Format this on a single string

#         if do_google_search is None: # If the chat is Travel related if not give static respond
#             return jsonify({"message": "Sorry, I can only responds to travel-related inquiries."})
#         summarized = filtered_summarizer(query, format_string) # Summerize for really good repond


#         response = summarized
#         # if not user_id or not query or not response:
#         #     return jsonify({"message": "Missing required parameters!"})

#         # Save response with a reference to the user_id
#         response_ref = realtime_database.child("responses").push({
#             # "user_id": user_id,
#             "query": query,
#             "response": response,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         })


#         return jsonify({"message": "Response saved!", "response":response, "response_ref": response_ref})




import logging



# Configure logging
logging.basicConfig(level=logging.INFO)

class UserResponse(Resource):
    def post(self):
        data = request.get_json()
        query = data.get("query")

        if not query:
            return jsonify({"message": "Missing query parameter!"})

        try:
            # Get the search query from the LLM
            search_query = configureOllama(query)
            
            # Perform the Google search
            do_google_search = google_search(search_query, my_cse_id, num=5, cr="us", lr="lang_en")

            if not do_google_search:
                return jsonify({"message": "No search results found or failed to get search results."})

            # Format the search results
            format_string = format_data(do_google_search)

            # Summarize the results
            summarized = filtered_summarizer(query, format_string)

            # Save the response to the database
            response_ref = realtime_database.child("responses").push({
                "query": query,
                "response": summarized,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            return jsonify({"message": "Response saved!", "response": summarized, "response_ref": response_ref})

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return jsonify({"message": "An error occurred while processing the request.", "error": str(e)})