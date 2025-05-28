from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from database import init_db

from routers import weather_router
import uvicorn

# from dotenv import load_dotenv
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d - %(funcName)s()] - %(message)s",
)
logger = logging.getLogger(__name__)

# load_dotenv()
app = FastAPI(title="Get weather")

main_router = APIRouter()


# main_router.include_router(llc_router, tags=["llc"])
main_router.include_router(weather_router, tags=["weather forecast"])


@main_router.get("/")
async def health_check():
    return {"Hello": "Mr. Anderson"}


# Инициализация БД при старте
@app.on_event("startup")
async def startup():
    init_db()


app.include_router(main_router)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
