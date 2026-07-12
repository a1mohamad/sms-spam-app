from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

SmsText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
    )
]


class PredictRequest(BaseModel):
    text: SmsText = Field(
        ...,
        description="SMS text to classify.",
    )


class PredictionResponse(BaseModel):
    label: Literal["ham", "spam"] = Field(
        ...,
        description="Predicted SMS class.",
    )
    spam_probability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Predicted probability of spam.",
    )