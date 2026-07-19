"""Async HTTP client for the UniFi Controller / Network API."""
from types import TracebackType
from typing import Any

import aiohttp

from app.core.logging import get_logger

logger = get_logger(__name__)


class UniFiError(Exception):
    """Raised on UniFi API communication errors."""


class UniFiClient:
    """Minimal async UniFi Controller client using cookie-based auth."""

    def __init__(
        self,
        host: str,
        port: int = 443,
        username: str = "",
        password: str = "",
        site: str = "default",
        verify_ssl: bool = False,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.site = site
        self.verify_ssl = verify_ssl
        self._session: aiohttp.ClientSession | None = None
        self._logged_in = False

    @property
    def base_url(self) -> str:
        return f"https://{self.host}:{self.port}"

    def _api_url(self, path: str) -> str:
        return f"{self.base_url}/api/s/{self.site}/{path.lstrip('/')}"

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(ssl=self.verify_ssl)
            self._session = aiohttp.ClientSession(connector=connector)
        return self._session

    async def login(self) -> bool:
        """Authenticate against the UniFi controller."""
        if not self.host or not self.username:
            raise UniFiError("UniFi host and username must be configured")
        session = await self._ensure_session()
        url = f"{self.base_url}/api/login"
        try:
            async with session.post(
                url,
                json={"username": self.username, "password": self.password},
            ) as resp:
                if resp.status != 200:
                    raise UniFiError(f"UniFi login failed with status {resp.status}")
                self._logged_in = True
                return True
        except aiohttp.ClientError as exc:
            raise UniFiError(f"UniFi login error: {exc}") from exc

    async def logout(self) -> None:
        """Log out and close the underlying session."""
        if self._session and not self._session.closed:
            try:
                if self._logged_in:
                    await self._session.post(f"{self.base_url}/api/logout")
            except aiohttp.ClientError:
                pass
            finally:
                await self._session.close()
        self._logged_in = False
        self._session = None

    async def _get(self, path: str) -> list[dict[str, Any]]:
        session = await self._ensure_session()
        if not self._logged_in:
            await self.login()
        url = self._api_url(path)
        try:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise UniFiError(f"GET {path} failed with status {resp.status}")
                body = await resp.json()
                return body.get("data", [])
        except aiohttp.ClientError as exc:
            raise UniFiError(f"GET {path} error: {exc}") from exc

    async def get_devices(self) -> list[dict[str, Any]]:
        return await self._get("stat/device")

    async def get_clients(self) -> list[dict[str, Any]]:
        return await self._get("stat/sta")

    async def get_events(self, limit: int = 200) -> list[dict[str, Any]]:
        return await self._get(f"stat/event?_limit={limit}")

    async def get_site_stats(self) -> dict[str, Any]:
        data = await self._get("stat/health")
        return {"health": data}

    async def get_network_config(self) -> list[dict[str, Any]]:
        return await self._get("rest/networkconf")

    async def get_firewall_rules(self) -> list[dict[str, Any]]:
        return await self._get("rest/firewallrule")

    async def get_port_forwards(self) -> list[dict[str, Any]]:
        return await self._get("rest/portforward")

    async def get_wlan_config(self) -> list[dict[str, Any]]:
        return await self._get("rest/wlanconf")

    async def get_routing(self) -> list[dict[str, Any]]:
        return await self._get("rest/routing")

    async def get_dns_settings(self) -> dict[str, Any]:
        settings = await self._get("rest/setting")
        dns = {}
        for entry in settings:
            if entry.get("key") == "dns" or "dns" in entry:
                dns.update(entry)
        return dns

    async def __aenter__(self) -> "UniFiClient":
        await self.login()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.logout()
