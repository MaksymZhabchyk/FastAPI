from fastapi import FastAPI
from app.routers import user, auth  # Додали auth
import uvicorn

# Можеш змінити назву на "Lab 5: Auth & JWT"
app = FastAPI(title="User CRUD & Auth Lab")

# Підключаємо роутери
app.include_router(user.router)
app.include_router(auth.router)

@app.get("/")
def path():
    return {"message": "API is running. Go to /docs for Swagger UI"}

if __name__ == "__main__":
    # Використовуємо порт 8080, як ми робили раніше
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)