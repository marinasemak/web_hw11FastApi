from fastapi import FastAPI

from src.users.routes import router as users_router
from src.auth.routes import router as auth_router
from src.contacts.routes import router as contacts_router
from src.contacts.routes import unexpected_exception_handler

app = FastAPI()


@app.get("/api/healthchecker")
async def healthcheck():
    return {"message": "Welcome to FastAPI!"}


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(contacts_router, prefix="/contacts", tags=["contacts"])
app.add_exception_handler(Exception, unexpected_exception_handler)
