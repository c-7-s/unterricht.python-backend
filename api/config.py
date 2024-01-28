from pydantic import BaseModel
from typing import List

class InterfaceConfig(BaseModel):
    upload_source_folder: str
    upload_allowed_formats: List[str]

interface_config = InterfaceConfig

interface_config.upload_source_folder = "docs/"
interface_config.upload_allowed_formats = ["txt", "pdf"]