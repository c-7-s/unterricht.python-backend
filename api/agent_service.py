from supabase.client import Client
from typing import Dict, Any, Tuple, List
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores.supabase import SupabaseVectorStore
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools.retriever import create_retriever_tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from langchain.utilities.tavily_search import TavilySearchAPIWrapper
from langchain.tools.tavily_search import TavilySearchResults
from langchain.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
import json

from utils.utils import initialize_environment_variables, initialize_subabase_client, initialize_openai_client
from utils.utils import initialize_tavily_client
import api.prompt_engineering  as pe
from api.config import interface_config


def get_uploaded_ids(supabase_client, filepath, upload_table_name):
    data, _cnt = supabase_client.table(upload_table_name).select('id').contains('metadata', {'source':filepath}).execute()
    return [data[1][i].get("id") for i in range(len(data[1]))]


def create_filter_list(context):
    uploaded_ids = []
    for doc in context:
        if len(doc) > 0:
            doc_uploaded_ids = get_uploaded_ids(doc, interface_config.upload_table_name)
            if len(doc_uploaded_ids) > 0:
                uploaded_ids += doc_uploaded_ids
    return uploaded_ids


def initialize_vector_store(client: Client, embedding: OpenAIEmbeddings, table_name: str, query_name: str) -> SupabaseVectorStore:
    vector_store = SupabaseVectorStore(
        client=client,
        embedding=embedding,
        table_name=table_name,
        query_name=query_name,
    )
    return vector_store


def get_answer(prompt_input):
    initialize_environment_variables("../.env")

    # Initialize Supabase Client
    supabase_client = initialize_subabase_client()

    # Initialize OpenAI Client
    _openai_client = initialize_openai_client()

    # Initialize Tavily Client
    _tavily_client = initialize_tavily_client()

    school_type, subject, topic, grade, state, keywords, context = pe.unpack_prompt_input(prompt_input)

    output_table_format = pe.create_output_table_format()
    
    task = pe.create_task_string(school_type, subject, topic, grade, state, output_table_format)

    embedding = OpenAIEmbeddings()
    vector_store = initialize_vector_store(supabase_client, embedding, interface_config.upload_table_name, interface_config.supabase_match_function)

    retrieved_context = vector_store.similarity_search(task, k=interface_config.context_k, filter=context)

    prompt = pe.pull_prompt_template(interface_config.prompt_template_name)

    search = TavilySearchAPIWrapper()
    tavily_tool = TavilySearchResults(api_wrapper=search, max_results=interface_config.tavily_max_response)

    wrapper = DuckDuckGoSearchAPIWrapper(region="de-de", time="d", max_results=5)
    duckduck = DuckDuckGoSearchResults(api_wrapper=wrapper)

    api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=100)
    wikipedia = WikipediaQueryRun(api_wrapper=api_wrapper)

    retriever = vector_store.as_retriever(search_type=interface_config.retriever_search_type, 
                                            search_kwargs={
                                                "k": int(round(len(context)/2,0)), # interface_config.retriever_k
                                                'lambda_mult': interface_config.retriever_mult, 
                                                'filter': {'uuid': context}
                                                }
                                            )

    retriever_tool = create_retriever_tool(
    retriever,
    "get_more_context",
    "A personal library optimized for user defined context information. Useful for when you need to know more about the given context. Input should be a search query.",
    )

    tools = [retriever_tool, tavily_tool, duckduck, wikipedia]

    llm = ChatOpenAI(model_name=interface_config.gpt_model_version, temperature=interface_config.gpt_model_temperature)
    agent = create_openai_functions_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    response = agent_executor.invoke({"input": task, "topic": topic, "retrieved_context": retrieved_context, "keywords": keywords, "chat_history": []})

    output = {}
    output["output"] = response["output"]

    output = json.dumps(output)

    return output

