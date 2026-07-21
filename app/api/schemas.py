from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

from app.core.config import AppConfig

SmsText = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=AppConfig.MAX_MESSAGE_LENGTH,
    )
]


class PredictRequest(BaseModel):
    """Represent a validated SMS classification request."""

    text: SmsText = Field(
        ...,
        description="SMS text to classify.",
    )


class PredictionResponse(BaseModel):
    """Represent the public result returned by the classifier."""

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
