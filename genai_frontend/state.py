from typing import TypedDict,Dict

class AgentState(TypedDict):
    srs_data: dict
    img_data: dict
    project_status: dict
    srs_path: str
    img_path: str