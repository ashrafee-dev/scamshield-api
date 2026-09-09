
from pydantic import ValidationError

from app.models.response import riskAssessment
from app.services.ai import ask_deepseek


def get_assessment(transcription: str) -> riskAssessment | None:
    for _ in range(5):
        response = ask_deepseek(transcription)

        if response is None:
            continue

        try:
            return riskAssessment(**response)

        except ValidationError as e:
            print(e.errors())

    return None
