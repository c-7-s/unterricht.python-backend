from supabase.client import Client
from typing import Dict, Any, Tuple, List
from langchain import hub
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores.supabase import SupabaseVectorStore
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools.retriever import create_retriever_tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from langchain.utilities.tavily_search import TavilySearchAPIWrapper
from langchain.tools.tavily_search import TavilySearchResults
import json

from utils.utils import initialize_environment_variables, initialize_subabase_client, initialize_openai_client
from utils.utils import initialize_tavily_client
from api.config import interface_config

def unpack_prompt_input(input: Dict[str, Any]) -> Tuple[str, str, str, str, List[str], List[str]]:
    school_type = str(input.get("subject"))
    subject = str(input.get("subject"))
    topic = str(input.get("topic"))
    grade = str(input.get("grade"))
    state = str(input.get("state"))
    keywords = [str(i) for i in input.get("keywords")]
    context = [str(i) for i in input.get("context")]
    return school_type, subject, topic, grade, state, keywords, context


def create_task_string(school_type: str, subject: str, topic: str, grade: str, state: str, keywords:List[str]) -> str:
    keywords = '\n'.join(keywords)
    return f"""
Schritt 1: Plane eine Unterrichtsstunde im Fach {subject} zum Thema {topic} für eine {grade} Klasse in {state} für den Schultyp {school_type} mit den Informationen aus Schritt 1 und Schritt 2.
Schritt 2: Formatiere deine Antwort in der folgenden json-Struktur:
______________________________

{{
    "learn_goals": "xyz",
    "table_data": [
        {{"title": "abc", "duration": "10min", "content": "blabla"}},
        {{...}},
        {{...}}
    ]
}}
______________________________

Los geht's!
"""


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


def create_prompt_template(retrieved_context: List[Any], keywords, topic, task: str) -> str:
    return f"""
Du bist ein Assistent für Lehrkräfte und deine Aufgabe ist Unterricht strukturiert, detailliert und fachlich korrekt vorzubereiten.
Alle Schritte der Aufgabe inklusive des Planens der Unterrichtsstunde müssen ohne Rückfragen ausgeführt werden.

Schlüsselbegriffe helfen dir bei der Lösung der Aufgabe den richtigen Fokus zu wählen.

Schlüsselbegriffe:
------------------
{topic}
{keywords}
------------------

Die Lehrkraft stellt dir Kontext zur Lösung der Aufgabe in deiner Bibliothek zur Verfügung. 
Hier ist ein kurzer Ausschnitt aus dem Kontext in deiner Bibliothek:

Ausschnitt aus dem Kontext:
---------
{retrieved_context}
---------

Die Gesamtlänge des Unterrichts soll insgesamt 45 Minuten betragen.

Aufgabe: 
{task}
"""

def get_answer(prompt_input):
    initialize_environment_variables("../.env")

    # Initialize Supabase Client
    supabase_client = initialize_subabase_client()

    # Initialize OpenAI Client
    _openai_client = initialize_openai_client()

    # Initialize Tavily Client
    _tavily_client = initialize_tavily_client()

    school_type, subject, topic, grade, state, keywords, context = unpack_prompt_input(prompt_input)

    task = create_task_string(school_type, subject, topic, grade, state, keywords)

    embedding = OpenAIEmbeddings()
    vector_store = initialize_vector_store(supabase_client, embedding, interface_config.upload_table_name, interface_config.supabase_match_function)

    retrieved_context = vector_store.similarity_search(task, k=interface_config.context_k, filter=context)

    prompt_template = create_prompt_template(retrieved_context, keywords, topic, task)

    prompt = hub.pull("hwchase17/openai-functions-agent")

    search = TavilySearchAPIWrapper()
    tavily_tool = TavilySearchResults(api_wrapper=search, max_results=interface_config.tavily_max_response)

    retriever = vector_store.as_retriever(search_type=interface_config.retriever_search_type, 
                                          search_kwargs={
                                              "k": interface_config.retriever_k,
                                              'lambda_mult': interface_config.retriever_mult, 
                                              'filter': {'uuid': context}
                                                }
                                            )

    retriever_tool = create_retriever_tool(
    retriever,
    "get_more_context",
    "A personal library optimized for user defined context information. Useful for when you need to know more about the given context. Input should be a search query.",
    )

    tools = [retriever_tool, tavily_tool]

    llm = ChatOpenAI(model_name=interface_config.gpt_model_version, temperature=interface_config.gpt_model_temperature)
    agent = create_openai_functions_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    response = agent_executor.invoke({"input": prompt_template})

    output = {}
    output["output"] = response["output"]

    output = json.dumps(output)

    return output

