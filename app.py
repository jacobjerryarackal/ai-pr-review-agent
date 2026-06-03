from fastapi import FastAPI

app = FastAPI(title="step-01-hello-fastapi")


@app.get("/health/live")
async def liveness():
    return {"status": "ok"}