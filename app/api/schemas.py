from typing import Literal

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
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