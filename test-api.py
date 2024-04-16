from fastapi import FastAPI

app = FastAPI()


@app.get("/data/{format}")
def read(format: str):
    with open(f"input/data.{format}", "r") as file:
        return file.read()


@app.post("/data/{destination}")
def write(destination: str, data: str):
    print(data)
    with open(f"output/{destination}", "w") as file:
        file.write(data)
