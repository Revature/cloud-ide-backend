import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "cloud_ide_celery",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.timezone = "UTC"

import app.tasks.starting_runner
import app.tasks.cleanup_runners

# Set up the beat schedule
celery_app.conf.beat_schedule = {
    # This job runs every 15 minutes
    "cleanup-active-runners": {
        "task": "app.tasks.cleanup_runners.cleanup_active_runners",
        "schedule": 900.0,  # 15 minutes in seconds
    },
}

## Start the Celery worker
# celery -A app.celery_app.celery_app worker --loglevel=info

# # In another terminal, start the Celery beat scheduler
# celery -A app.celery_app.celery_app beat --loglevel=info