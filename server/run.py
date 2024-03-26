import uvicorn
import os

uvicorn.run(
    "main:app",
    reload=False,
    host="0.0.0.0",
    port=5400,
)

