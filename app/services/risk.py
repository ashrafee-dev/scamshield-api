import json

from openai import OpenAIError
from pydantic import ValidationError

from app.models.response import riskAssessment
from app.services.ai import ask_deepseek


class AssessmentUnavailable(RuntimeError):
    """The upstream assessment service could not complete the request."""


def get_assessment(transcription: str) -> riskAssessment:
    for _ in range(2):
        try:
            response = ask_deepseek(transcription)
            return riskAssessment.model_validate(response)
        except (ValidationError, json.JSONDecodeError):
            continue
        except OpenAIError as exc:
            raise AssessmentUnavailable("Assessment provider unavailable") from exc
    raise AssessmentUnavailable("Assessment provider returned an invalid response")
