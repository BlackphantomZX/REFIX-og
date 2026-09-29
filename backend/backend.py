"""
FastAPI application entry point.

Run locally from the backend/ directory with:

    python3 -m uvicorn backend:app --reload

The ASGI app object MUST be named `app` (not `backend`) so that command
works as-is.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config
from routes import devices, estimates, repairs

app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description=(
        "Public, anonymous mobile repair cost estimator API. No authentication, "
        "no personal data collection. Pricing data is a sample dataset for "
        "prototyping and should be replaced with verified figures before production use."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["health"])
def health_check():
    return {"status": "ok", "service": config.APP_NAME, "version": config.APP_VERSION}


app.include_router(devices.router)
app.include_router(repairs.router)
app.include_router(estimates.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend:app", host=config.HOST, port=config.PORT, reload=True)
