"""Graph node dependencies."""

from dataclasses import dataclass, field

from agent.llm.base import LLMProvider
from agent.tools.browser_client import BrowserClient
from agent.tools.memory_client import MemoryClient
from agent.tools.search_client import SearchClient


@dataclass
class NodeContext:
    llm: LLMProvider
    search: SearchClient = field(default_factory=SearchClient)
    browser: BrowserClient = field(default_factory=BrowserClient)
    memory: MemoryClient | None = None

    def __post_init__(self) -> None:
        if self.memory is None:
            self.memory = MemoryClient(self.llm)
