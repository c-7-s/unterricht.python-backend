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
    return f"""Plane eine Unterrichtsstunde im Fach {subject} zum Thema {topic} für eine {grade} Klasse in {state} für den Schultyp {school_type}.
Lege bei dieser Aufgabe einen besonderen Fokus auf die folgenden Schlüsselbegriffe:
    
Schlüsselbegriffe:
------------------
{keywords}
------------------"""


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


def create_prompt_template(retrieved_context: List[Any], task: str) -> str:
    return f"""
Du bist ein Assistent für Lehrende und deine Aufgabe ist Unterricht nach den höchsten Standards vorzubereiten. 
Schlüsselwöter helfen dir bei der Lösung der Aufgabe den Fokus richtig zu wählen.
Die Lehrkraft stellt dir wichtigen Kontext zur Lösung der Aufgabe in deiner Bibliothek zur Verfügung. 
Die Lösung der Aufgabe soll in jedem Fall eine inhaltliche und zeitliche Struktur für den Unterricht beinhalten.
Wenn du keine Lösung findest, sage einfach, dass du die Aufgabe nicht lösen kannst, und versuche keine Antwort zu erfinden.
Hier ist ein relevanter Ausschnitt aus dem Kontext aus deiner Bibliothek:

Ausschnitt aus dem Kontext:
---------
{retrieved_context}
---------

Los geht's!

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

    retrieved_context = vector_store.similarity_search(task, k=2, filter=context)

    prompt_template = create_prompt_template(retrieved_context, task)

    prompt = hub.pull("hwchase17/openai-functions-agent")

    search = TavilySearchAPIWrapper()
    tavily_tool = TavilySearchResults(api_wrapper=search, max_results=5)

    retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 4, 'lambda_mult': 0.25, 'filter': {'uuid': context}})

    retriever_tool = create_retriever_tool(
    retriever,
    "get_more_context",
    "A personal library optimized for the most relevant results. Useful for when you need to know more about the given context. Input should be a search query.",
    )

    tools = [retriever_tool, tavily_tool]

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
    agent = create_openai_functions_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True)

    response = agent_executor.invoke({"input": prompt_template})

    context_dict = [doc.dict() for doc in retrieved_context]

    output = {}
    output["input"] = response["input"]
    output["ouput"] = response["output"]
    output["context"] = context_dict

    return output

