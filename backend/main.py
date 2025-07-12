from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to LinkLine backend!"}

# TODO: Add endpoint for research study submission
