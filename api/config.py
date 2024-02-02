from pydantic import BaseModel
from typing import List

class InterfaceConfig(BaseModel):
    upload_allowed_formats: List[str]
    upload_table_name: str
    supabase_match_function: str
    gpt_model_version: str
    gpt_model_temperature: float
    context_k: int
    retriever_k: int
    retriever_mult: float

interface_config = InterfaceConfig(
    upload_allowed_formats=["txt", "pdf"],
    upload_table_name="vector_store",
    supabase_match_function="match_documents_with_uuid_filter",
    gpt_model_version="gpt-3.5-turbo-1106",
    gpt_model_temperature=0.7,
    context_k=3,
    retriever_k=5,
    retriever_mult=0.25,

)
