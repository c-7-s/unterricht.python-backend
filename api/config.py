from pydantic import BaseModel
from typing import List

class InterfaceConfig(BaseModel):
    upload_allowed_formats: List[str]
    upload_table_name: str
    supabase_match_function: str 

interface_config = InterfaceConfig(
    upload_allowed_formats=["txt", "pdf"],
    upload_table_name="vector_store",
    supabase_match_function="match_documents_with_uuid_filter"
)
