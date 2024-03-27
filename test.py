from fastapi import FastAPI
app = FastAPI()

def run():

    print(1)

    @app.get("/")
    def read_root():
        return {"Hello": "World"}


run()