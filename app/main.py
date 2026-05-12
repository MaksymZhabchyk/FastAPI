from fastapi import FastAPI
from app.routers import user
import uvicorn


app = FastAPI(title="User CRUD Lab")

app.include_router(user.router)

@app.get("/")
def path():
    return {"Hello": "World"}

if __name__ == "__main__":

    uvicorn.run("main:app", host="0.0.0.0", port=8000)