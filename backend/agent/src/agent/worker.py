"""Redis queue worker for agent graph execution."""

import asyncio
import uuid

from langgraph.errors import GraphInterrupt

from agent.graph.runner import GraphRunner
from agent.logging_config import get_logger, setup_logging
from agent.persistence.database import async_session_factory
from agent.persistence.models import ExecutionStatus
from agent.persistence.repository import ExecutionRepository
from agent.queue.redis_queue import AgentJob, JobType, RedisQueue

logger = get_logger(__name__)

STARTUP_RETRIES = 30
STARTUP_DELAY_SECONDS = 2


async def process_job(runner: GraphRunner, queue: RedisQueue, job: AgentJob) -> None:
    execution_id = uuid.UUID(job.execution_id)
    log_extra = {"execution_id": job.execution_id}

    if not await queue.acquire_lock(job.execution_id):
        logger.warning("Could not acquire lock, skipping job", extra=log_extra)
        return

    try:
        async with async_session_factory() as session:
            repo = ExecutionRepository(session)
            execution = await repo.get_execution(execution_id)
            if execution is None:
                logger.error("Execution not found", extra=log_extra)
                return

            if job.job_type == JobType.RUN:
                await runner.run(repo, execution_id, execution.goal)
            elif job.job_type == JobType.RESUME:
                await runner.run(repo, execution_id, execution.goal, resume=True)
            elif job.job_type == JobType.CONTINUE:
                await runner.run(
                    repo,
                    execution_id,
                    execution.goal,
                    human_response=job.human_response,
                )

            await queue.publish_event(job.execution_id, {"event": "completed"})

    except GraphInterrupt:
        logger.info("Graph interrupted for human input", extra=log_extra)
        async with async_session_factory() as session:
            repo = ExecutionRepository(session)
            await repo.update_execution(
                execution_id,
                status=ExecutionStatus.WAITING_HUMAN_INPUT.value,
            )
        await queue.publish_event(job.execution_id, {"event": "waiting_human_input"})

    except Exception as exc:
        logger.exception("Job failed: %s", exc, extra=log_extra)
        async with async_session_factory() as session:
            repo = ExecutionRepository(session)
            await repo.update_execution(
                execution_id,
                status=ExecutionStatus.FAILED.value,
                error_message=str(exc),
            )
        await queue.publish_event(job.execution_id, {"event": "failed", "error": str(exc)})

    finally:
        await queue.release_lock(job.execution_id)


async def run_worker() -> None:
    setup_logging()
    queue = RedisQueue()
    await queue.connect()
    runner = GraphRunner()

    for attempt in range(1, STARTUP_RETRIES + 1):
        try:
            await runner.initialize()
            break
        except Exception as exc:
            if attempt >= STARTUP_RETRIES:
                logger.exception("Failed to initialize worker after %s attempts", STARTUP_RETRIES)
                raise
            logger.warning(
                "Worker startup waiting for dependencies (attempt %s/%s): %s",
                attempt,
                STARTUP_RETRIES,
                exc,
            )
            await asyncio.sleep(STARTUP_DELAY_SECONDS)

    logger.info("Agent worker started")

    while True:
        job = await queue.dequeue(timeout=5)
        if job is None:
            continue
        logger.info("Processing job %s for execution %s", job.job_type, job.execution_id)
        await process_job(runner, queue, job)


def main() -> None:
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
