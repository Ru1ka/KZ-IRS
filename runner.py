import uvicorn
import os

uvicorn.run(
    "test:app",
    reload=False,
    host="127.0.0.1",
    port=5401,
)

