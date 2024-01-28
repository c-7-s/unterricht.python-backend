from pydantic import BaseModel
from typing import List


class InterfaceConfig(BaseModel):
    upload_source_folder: str
    upload_allowed_formats: List[str]

