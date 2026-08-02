from fastapi import FastAPI

app = FastAPI(
    title="Schema Drift Intelligence Platform",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Schema Drift Platform Running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }