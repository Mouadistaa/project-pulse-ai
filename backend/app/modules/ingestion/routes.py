from fastapi import APIRouter, Depends, HTTPException
from redis import Redis
from rq import Queue
from app.core.config import settings
from app.modules.users.routes import get_current_admin_user
from app.modules.users.schemas import User

router = APIRouter()

@router.post("/jobs/sync")
async def enqueue_sync_job(
    current_user: User = Depends(get_current_admin_user)
):
    # Connect to Redis
    redis_conn = Redis.from_url(settings.REDIS_URL)
    q = Queue(connection=redis_conn)
    
    # Enqueue the job
    from app.modules.ingestion.jobs import sync_data_job
    job = q.enqueue(sync_data_job)
    
    return {"job_id": job.get_id(), "status": "enqueued"}
