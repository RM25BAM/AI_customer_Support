from langchain_ollama import OllamaLLM
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_core.prompts import PromptTemplate



def configureOllama(query):
    if is_travel_related(query) == False:
        return None
    model = OllamaLLM(model="llama3.1")
    response_schema = [ResponseSchema(name="search_query", description="Provide the best 1 Google search query related to the user's question")]

    output_parser = StructuredOutputParser.from_response_schemas(response_schema)
    format_instructions = output_parser.get_format_instructions()
    prompt = PromptTemplate(
        template="answer the users question as best as possible.\n{format_instructions}\n{question}",
        input_variables=["question"],
        partial_variables={"format_instructions": format_instructions},
    )
    chain = prompt | model | output_parser
    
    result = chain.invoke({"question": query})

    return result # {'search_query': ['Iceland travel accommodations']}



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
            "Summarize the following paragraphs into one cohesive summary and provide information relevant to the user's query.\n"
            "{format_instructions}\n\n"
            "Query: {query}\n\n"
            "Paragraphs:\n{paragraphs}"
        ),
        input_variables=["query", "summary"],
        partial_variables={"format_instructions": format_instructions},
    )
    
    chain = prompt | model | output_parser
    result = chain.invoke({"query": query, "summary": paragraph})
    
    return result # response['summary'], response['related']


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

    # Setup the parser output parser and prompt
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

    chain = prompt | model | output_parser

    result = chain.invoke({"query": query})

    is_related = result["travel_related"].strip().lower() == 'yes'

    if is_related == 'yes':
        return result  # Return the result with the travel-related information and category
    else:
        return None  # Return None if the query is not travel-related
