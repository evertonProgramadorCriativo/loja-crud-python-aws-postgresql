from fastapi import FastAPI

from app.routers import auth, products

app = FastAPI(title="Loja CRUD")
app.include_router(auth.router)
app.include_router(products.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
