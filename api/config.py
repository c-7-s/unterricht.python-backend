from pydantic import BaseModel
from typing import List

class InterfaceConfig(BaseModel):
    upload_allowed_formats: List[str]
    upload_table_name: str

interface_config = InterfaceConfig

interface_config.upload_allowed_formats = ["txt", "pdf"]
interface_config.upload_table_name = "vector_store"