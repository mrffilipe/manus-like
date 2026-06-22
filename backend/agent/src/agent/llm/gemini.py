"""Gemini LLM adapter."""

import json
import uuid
from typing import Any

from google import genai
from google.genai import types

from agent.config import settings
from agent.llm.base import LLMProvider, LLMResponse, Message, Tool, ToolCall


class GeminiProvider:
    def __init__(self) -> None:
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_model
        self.embedding_model = settings.gemini_embedding_model

    def _to_gemini_contents(self, messages: list[Message]) -> list[types.Content]:
        contents: list[types.Content] = []
        for msg in messages:
            if msg.role == "system":
                contents.append(
                    types.Content(
                        role="user",
                        parts=[types.Part(text=f"[SYSTEM]\n{msg.content}")],
                    )
                )
            elif msg.role == "user":
                contents.append(types.Content(role="user", parts=[types.Part(text=msg.content)]))
            elif msg.role == "assistant":
                contents.append(types.Content(role="model", parts=[types.Part(text=msg.content)]))
            elif msg.role == "tool":
                contents.append(
                    types.Content(
                        role="user",
                        parts=[types.Part(text=f"[TOOL:{msg.name}]\n{msg.content}")],
                    )
                )
        return contents

    def _to_gemini_tools(self, tools: list[Tool] | None) -> list[types.Tool] | None:
        if not tools:
            return None
        declarations = []
        for tool in tools:
            declarations.append(
                types.FunctionDeclaration(
                    name=tool.name,
                    description=tool.description,
                    parameters=tool.parameters,
                )
            )
        return [types.Tool(function_declarations=declarations)]

    async def chat(
        self,
        messages: list[Message],
        tools: list[Tool] | None = None,
    ) -> LLMResponse:
        config_kwargs: dict[str, Any] = {}
        gemini_tools = self._to_gemini_tools(tools)
        if gemini_tools:
            config_kwargs["tools"] = gemini_tools

        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=self._to_gemini_contents(messages),
            config=types.GenerateContentConfig(**config_kwargs) if config_kwargs else None,
        )

        content = ""
        tool_calls: list[ToolCall] = []

        if response.candidates and response.candidates[0].content:
            for part in response.candidates[0].content.parts or []:
                if part.text:
                    content += part.text
                if part.function_call:
                    fc = part.function_call
                    args = dict(fc.args) if fc.args else {}
                    tool_calls.append(
                        ToolCall(
                            id=str(uuid.uuid4()),
                            name=fc.name or "unknown",
                            arguments=args,
                        )
                    )

        return LLMResponse(content=content.strip(), tool_calls=tool_calls)

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        result = await self.client.aio.models.embed_content(
            model=self.embedding_model,
            contents=texts,
        )
        embeddings: list[list[float]] = []
        for emb in result.embeddings or []:
            embeddings.append(list(emb.values))
        return embeddings


def get_llm_provider() -> LLMProvider:
    return GeminiProvider()
