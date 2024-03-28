from fastapi import FastAPI
import uvicorn

app = FastAPI()

p1 = '9,4,1488;10,4,1488;'
p2 = '9,9,1488;9,10,1488;'
p3 = '4,9,1488;3,9,1488;'

@app.get("/robot/pos")
def robotPing():
    s = '0,0,0;'
    s += p3
    return s

if __name__ == '__main__':
    uvicorn.run("server:app", host="0.0.0.0", port=5400)