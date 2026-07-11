from fastapi import FastAPI

app = FastAPI(
    title="SMS Spam Classifier",
    description="API for classifying SMS messages as ham or spam.",
    version="1.0.0",
)

@app.get("/health")
def health_check() -> dict[str, str]:
    """
    Health check endpoint to verify that the API is running.

    Returns:
        dict: A dictionary containing the status of the API.
    """
    return {"status": "ok"}