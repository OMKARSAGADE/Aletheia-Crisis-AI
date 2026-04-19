from typing import TypedDict

class CrisisState(TypedDict):
    input_text: str
    extracted_data: dict
    verification_result: dict
    risk_result: dict
    action_result: dict
    summary_result: dict
