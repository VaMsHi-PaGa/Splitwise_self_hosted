from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler
import logging

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.seed import seed_demo_data
from app.routers import auth, users, groups, expenses, balances, settlements, recurring, exports
from app.services.recurring_runner import run_recurring_tasks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def init_db():
    Base.metadata.create_all(bind=engine)
    if settings.seed_demo:
        db = SessionLocal()
        try:
            seed_demo_data(db)
            logger.info("Seeded demo data")
        finally:
            db.close()


def start_scheduler():
    scheduler.add_job(recurring_job, "interval", hours=1, id="recurring_tasks")
    scheduler.start()
    logger.info("Scheduler started")


def recurring_job():
    db = SessionLocal()
    try:
        run_recurring_tasks(db)
    except Exception as e:
        logger.error(f"Error running recurring tasks: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_db()
    except Exception as e:
        logger.error(f"init_db failed: {e}")
    try:
        start_scheduler()
    except Exception as e:
        logger.error(f"scheduler failed to start: {e}")
    logger.info("Application started")
    yield
    try:
        scheduler.shutdown()
    except Exception:
        pass
    logger.info("Application shutdown")


app = FastAPI(title="SplitSmart India", lifespan=lifespan)

cors_origins = settings.cors_origins_list
allow_credentials = "*" not in cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(groups.router)
app.include_router(expenses.router)
app.include_router(balances.router)
app.include_router(settlements.router)
app.include_router(recurring.router)
app.include_router(exports.router)


@app.get("/health")
def health():
    return {"status": "ok"}
