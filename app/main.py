from fastapi import FastAPI

from app.routers import auth

app = FastAPI(title="Loja CRUD")
app.include_router(auth.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
