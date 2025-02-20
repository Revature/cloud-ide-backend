import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlmodel import Session
from app.db.database import engine
from app.models.some_model import SomeModel  # Replace with your model if needed

scheduler = AsyncIOScheduler()

def cleanup_database():
    with Session(engine) as session:
        logging.info("Running cleanup job...")
        session.commit()

def start_scheduler():
    # Schedule the cleanup job to run every 15 minutes.
    trigger = IntervalTrigger(minutes=15)
    scheduler.add_job(cleanup_database, trigger)
    scheduler.start()
    logging.info("Scheduler started with a 15-minute interval.")