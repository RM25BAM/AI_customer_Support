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
    # Define a list of travel-related keywords
    model = OllamaLLM(model="llama3.1")

    response_schema = ResponseSchema(
        name="travel_related",
        description="Indicate whether the given query is related to travel. Respond with 'yes' or 'no'."
    )

    #Setup the parser output parser and prompt
    output_parser = StructuredOutputParser.from_response_schemas([response_schema])
    format_instructions = output_parser.get_format_instructions()

    prompt = PromptTemplate(
        template=(
            "Determine if the following query is related to travel.\n"
            "{format_instructions}\n\n"
            "Query: {query}"
        ),
        input_variables=["query"],
        partial_variables={"format_instructions": format_instructions}
    )

    chain = prompt | model | output_parser

    result = chain.invoke({"query": query})

    is_related = result["travel_related"].strip().lower() == 'yes'

    return is_related