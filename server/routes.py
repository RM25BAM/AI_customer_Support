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
from googleapiclient.discovery import build

# Load environment variables
load_dotenv('server/.env.dev')

# Initialize Firebase database and storage
auth, realtime_database, storage = database_authentication()

# Google Search API setup
my_cse_id = "f188e2180323e449e"
dev_key = os.getenv("GOOGLE_SEARCH_API_KEY")

def is_travel_related(query):

    # Instantiate the model
    model = OllamaLLM(model="llama3.1")

    # Define the response schemas for determining if the query is travel-related and categorizing it
    travel_related_schema = ResponseSchema(
        name="travel_related",
        description="Indicate whether the given query is related to travel, including destinations, accommodations, activities, food and drink, visa requirements, and other travel-related topics. Respond with 'yes' or 'no'."
    )

    category_schema = ResponseSchema(
        name="category",
        description="If the query is travel-related, specify the category such as 'Destinations', 'Accommodations', 'Activities', 'Food and Drink', or 'Visa and Travel Requirements'."
    )

    # Setup the output parser and prompt
    output_parser = StructuredOutputParser.from_response_schemas([travel_related_schema, category_schema])
    format_instructions = output_parser.get_format_instructions()

    prompt = PromptTemplate(
        template=(
            "Determine if the following query is related to travel or any travel-related topics, such as:\n"
            "- Destinations (cities, countries, specific attractions)\n"
            "- Accommodations (hotels, lodgings)\n"
            "- Activities (sightseeing, tours, events)\n"
            "- Food and drink (restaurants, local cuisines)\n"
            "- Visa and travel requirements (passports, entry regulations)\n"
            "- Other topics directly related to planning or enjoying a trip.\n"
            "Respond 'no' if it is not related to travel. If 'yes', also categorize it into one of the following: 'Destinations', 'Accommodations', 'Activities', 'Food and Drink', 'Visa and Travel Requirements'.\n"
            "{format_instructions}\n\n"
            "Query: {query}"
        ),
        input_variables=["query"],
        partial_variables={"format_instructions": format_instructions}
    )

    # Execute the prompt chain
    chain = prompt | model | output_parser
    result = chain.invoke({"query": query})

    # Check if the query is travel-related
    is_related = result["travel_related"].strip().lower()

    if is_related == 'yes':
        return result  # Return the result with travel-related information and category
    else:
        return {
            "message": "This query is not related to travel. Please ask a travel-related question."
        }


def google_search(search_term, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=dev_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    result = res.get('items', [])
    
    # Filter or rank results based on relevance (e.g., based on keywords in the query)
    filtered_results = {}
    for index, item in enumerate(result[:5]):  # Limit to top 5 results for relevance
        title = item.get('title')
        link = item.get('link')
        snippet = item.get("snippet")
        filtered_results[index] = [title, link, snippet]

    return filtered_results


def filtered_summarizer(query, paragraphs):
    # Instantiate the model
    model = OllamaLLM(model="llama3.1")

    # Define the response schema for the summary
    response_schema = [
        ResponseSchema(name="summary", description="A concise summary relevant to the user's query."),
    ]

    # Setup the output parser and prompt
    output_parser = StructuredOutputParser.from_response_schemas(response_schema)
    format_instructions = output_parser.get_format_instructions()

    prompt = PromptTemplate(
        template=(
            "You are a travel assistant. Given the user's query and the following paragraphs, "
            "summarize the key points most relevant to the user's travel-related inquiry.\n"
            "{format_instructions}\n\n"
            "Query: {query}\n\n"
            "Paragraphs:\n{paragraphs}"
        ),
        input_variables=["query", "paragraphs"],
        partial_variables={"format_instructions": format_instructions},
    )

    # Execute the prompt chain
    chain = prompt | model | output_parser
    result = chain.invoke({"query": query, "paragraphs": paragraphs})

    # Get the summary result
    summary = result['summary']

    # Formulate the response with an offer for further assistance
    response = (
        f"Summary: {summary}\n\n"
        "Would you like more information or resources related to this topic? "
        "I can help you find accommodations, activities, or other travel-related services."
    )

    return response


class UserResponse(Resource):
    def post(self):
        data = request.get_json()
        query = data.get("query")
        
        # Validate and filter the query
        if not is_travel_related(query):
            return jsonify({"message": "This query is not related to travel."})
        
        # Generate the search query and perform the search
        search_query = configureOllama(query)
        google_results = google_search(search_query, my_cse_id, num=5, cr="us", lr="lang_en")
        
        if not google_results:
            return jsonify({"message": "No relevant results found."})

        # Summarize the results
        summarized_response = filtered_summarizer(query, google_search)

        # Save the response in the database
        response_ref = realtime_database.child("responses").push({
            "query": query,
            "response": summarized_response,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        return jsonify({
            "message": "Response generated successfully!",
            "links":[link[1] for _, link in google_results.items()],
            "response": summarized_response,
            "response_ref": response_ref
        })
