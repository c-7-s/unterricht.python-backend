import os
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores.supabase import SupabaseVectorStore
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import OpenAI
from langchain.output_parsers import RegexParser
from supabase.client import create_client, Client
from dotenv import load_dotenv

load_dotenv("../.env")

# Initialize Supabase Client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_API_KEY")
supabase_client: Client = create_client(url, key)

# Initialize OpenAI Client
opeani_key = url = os.environ.get('OPENAI_KEY')
client = OpenAI(api_key=opeani_key)

prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

This should be in the following format:

Question: [question here]
Helpful Answer: [answer here]
Score: [score between 0 and 100]

Begin!

Context:
---------
{context}
---------
Question: {question}
Helpful Answer:"""
output_parser = RegexParser(
    regex=r"(.*?)\nScore: (.*)",
    output_keys=["answer", "score"],
)
PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"],
    output_parser=output_parser
)
chain = load_qa_chain(OpenAI(temperature=1), chain_type="map_rerank", return_intermediate_steps=True, prompt=PROMPT)


def getanswer(query):
    embeddings = OpenAIEmbeddings()
    vector_store = SupabaseVectorStore(
        client=supabase_client,
        embedding=embeddings,
        table_name="documents_new",
    )
    query_embeddings = embeddings.embed_query(query)
    relevant_chunks = vector_store.similarity_search_by_vector_with_relevance_scores(query_embeddings,k=2)
    chunk_docs=[]
    for chunk in relevant_chunks:
        chunk_docs.append(chunk[0])
    results = chain({"input_documents": chunk_docs, "question": query})
    text_reference=""
    for i in range(len(results["input_documents"])):
        text_reference+=results["input_documents"][i].page_content
    output={"Answer":results["output_text"],"Reference":text_reference}
    return output