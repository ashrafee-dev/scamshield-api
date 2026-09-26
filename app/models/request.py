from pydantic import BaseModel, ConfigDict, Field


class TextRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    body: str = Field(min_length=1, max_length=10_000)


class information(TextRequest):
    """Legacy /email payload; sender is accepted but is not used in assessment."""
    sender: str | None = Field(default=None, max_length=320)
