import os
from typing import Any, Dict, List, Optional

import httpx
from fastmcp import FastMCP
from fastapi import Body
from starlette.responses import JSONResponse, PlainTextResponse
from config.settings import NOTION_API_KEY


class NotionSettings:
    BASE_URL = "https://api.notion.com/v1"
    VERSION = "2024-06-28"

    def __init__(self):
        self.token = NOTION_API_KEY
        if not self.token:
            raise RuntimeError("NOTION_TOKEN not set")

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": self.VERSION,
            "Content-Type": "application/json",
        }


class AsyncHttpClient:
    def __init__(self, base_url: str, headers: Dict[str, str]):
        self.base_url = base_url
        self.headers = headers

    async def get(self, path: str, params: Optional[Dict[str, Any]] = None):
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(
                f"{self.base_url}{path}",
                headers=self.headers,
                params=params,
            )
        return self._normalize(r)

    async def post(self, path: str, body: Dict[str, Any]):
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                f"{self.base_url}{path}",
                headers=self.headers,
                json=body,
            )
        return self._normalize(r)

    async def patch(self, path: str, body: Dict[str, Any]):
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.patch(
                f"{self.base_url}{path}",
                headers=self.headers,
                json=body,
            )
        return self._normalize(r)

    def _normalize(self, response: httpx.Response):
        try:
            payload = response.json()
        except Exception:
            payload = {"text": response.text}

        return {
            "ok": response.is_success,
            "status_code": response.status_code,
            "data": payload if response.is_success else None,
            "error": None if response.is_success else payload,
        }


class NotionClient:
    def __init__(self, http: AsyncHttpClient):
        self.http = http

    async def create_page(
        self,
        parent_page_id: str,
        title: str,
        properties: Optional[Dict[str, Any]] = None,
        children: Optional[List[Dict[str, Any]]] = None,
    ):
        body = {
            "parent": {"page_id": parent_page_id},
            "properties": properties
            or {
                "title": {
                    "title": [{"type": "text", "text": {"content": title}}]
                }
            },
        }

        if children:
            body["children"] = children

        return await self.http.post("/pages", body)

    async def update_page(
        self,
        page_id: str,
        properties: Optional[Dict[str, Any]] = None,
        archived: Optional[bool] = None,
    ):
        payload = {}

        if properties is not None:
            payload["properties"] = properties

        if archived is not None:
            payload["archived"] = archived

        if not payload:
            return {
                "ok": False,
                "status_code": 400,
                "error": "No update fields provided",
            }

        return await self.http.patch(f"/pages/{page_id}", payload)

    async def get_page(self, page_id: str):
        return await self.http.get(f"/pages/{page_id}")

    async def append_block_children(
        self,
        block_id: str,
        children: List[Dict[str, Any]],
    ):
        return await self.http.patch(
            f"/blocks/{block_id}/children",
            {"children": children},
        )

    async def archive_page(self, page_id: str):
        return await self.update_page(page_id, archived=True)


class NotionMCPServer:
    def __init__(self):
        settings = NotionSettings()
        http_client = AsyncHttpClient(
            base_url=settings.BASE_URL,
            headers=settings.headers,
        )
        self.notion = NotionClient(http_client)
        self.mcp = FastMCP("NotionConnector")
        self._register_tools()
        self._register_routes()

    def _register_tools(self):
        @self.mcp.tool()
        async def create_page(**kwargs):
            return await self.notion.create_page(**kwargs)

        @self.mcp.tool()
        async def update_page(**kwargs):
            return await self.notion.update_page(**kwargs)

        @self.mcp.tool()
        async def get_page(page_id: str):
            return await self.notion.get_page(page_id)

        @self.mcp.tool()
        async def append_block_children(**kwargs):
            return await self.notion.append_block_children(**kwargs)

        @self.mcp.tool()
        async def archive_page(page_id: str):
            return await self.notion.archive_page(page_id)

    def _register_routes(self):
        @self.mcp.custom_route("/health", methods=["GET"])
        async def health(_):
            return PlainTextResponse("OK")

        @self.mcp.custom_route("/tools", methods=["GET"])
        async def list_tools(_):
            return JSONResponse(
                {
                    "tools": [
                        "create_page",
                        "update_page",
                        "get_page",
                        "append_block_children",
                        "archive_page",
                    ]
                }
            )

        @self.mcp.custom_route("/tools/{tool_name}", methods=["POST"])
        async def call_tool(_, tool_name: str, body=Body(...)):
            try:
                handler = getattr(self.notion, tool_name)
                result = await handler(**body)
                return JSONResponse(result)
            except AttributeError:
                return JSONResponse(
                    {"error": "Unknown tool"},
                    status_code=400,
                )
            except Exception as e:
                return JSONResponse(
                    {"error": str(e)},
                    status_code=500,
                )

    def run(self):
        self.mcp.run(transport="http")


if __name__ == "__main__":
    NotionMCPServer().run()
