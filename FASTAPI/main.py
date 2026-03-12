from fastapi import FastAPI
from myapi import router as myapi_router
from imageapi import router as image_router
from history import router as history_router
from Quiz import router as Quiz_router

app = FastAPI()

app.include_router(myapi_router)
app.include_router(image_router)
app.include_router(history_router)
app.include_router(Quiz_router)





