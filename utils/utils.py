import os
from supabase.client import create_client, Client
from langchain_openai import OpenAI
from tavily import TavilyClient
from dotenv import load_dotenv

def initialize_environment_variables(path_to_file: str) -> None:
    return load_dotenv(path_to_file)

def initialize_subabase_client() -> Client:
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_API_KEY")
    return create_client(url, key)

def initialize_openai_client() -> OpenAI:
    openai_key = os.environ.get('OPENAI_KEY')
    return OpenAI(api_key=openai_key)

def initialize_tavily_client() -> TavilyClient:
    key: str = os.environ.get("TAVILY_API_KEY")
    return TavilyClient(api_key=key)