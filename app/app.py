from fastapi import FastAPI
from app.users.routes import user_router

def create_application() -> FastAPI:
    application = FastAPI()
    application.include_router(user_router)
    return application

app = create_application()

@app.get("/")
async def root():
    return {"message": "App was running successfully...!"}
