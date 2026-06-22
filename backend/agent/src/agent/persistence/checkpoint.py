"""LangGraph Postgres checkpoint saver."""

from contextlib import AsyncExitStack

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from agent.config import settings


class CheckpointManager:
    def __init__(self) -> None:
        self._stack = AsyncExitStack()
        self.checkpointer: AsyncPostgresSaver | None = None

    async def setup(self) -> AsyncPostgresSaver:
        if self.checkpointer is not None:
            return self.checkpointer

        conn_string = settings.database_url_checkpoint
        saver = AsyncPostgresSaver.from_conn_string(conn_string)
        self.checkpointer = await self._stack.enter_async_context(saver)
        await self.checkpointer.setup()
        return self.checkpointer

    async def close(self) -> None:
        await self._stack.aclose()
        self.checkpointer = None


checkpoint_manager = CheckpointManager()
