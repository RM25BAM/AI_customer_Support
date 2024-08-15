from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from server.ai_setup import LLAMA2LLM
from dotenv import load_dotenv
import os


load_dotenv('server/.env.dev')

OPENROUTER_API_KEY=os.getenv('OPENROUTER_API_KEY')








