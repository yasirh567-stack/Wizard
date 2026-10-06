from fastapi import FastAPI

from app.api.routes import accounts, auth, categories, demo, plaid, transactions

app = FastAPI(title="Wizard API")

app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(plaid.router)
app.include_router(demo.router)
app.include_router(categories.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
