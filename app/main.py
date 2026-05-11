from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def main():
    return {"Hello": "World"}

if __name__ == "__main__":
    main()