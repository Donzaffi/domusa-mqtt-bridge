import aiohttp


class DomusaAPI:
    def __init__(self, auth):
        self.base = "https://ic-api-app.azurewebsites.net/api"
        self.auth = auth
        self.token = None

    async def _get_headers(self):
        if not self.token:
            self.token = await self.auth.get_token()

        if not self.token:
            return None

        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def _request(self, method, url, json_data=None):
        headers = await self._get_headers()

        if not headers:
            print("ERROR: No authentication token available")
            return None

        try:
            timeout = aiohttp.ClientTimeout(total=10)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                # First request
                async with session.request(
                    method,
                    url,
                    headers=headers,
                    json=json_data,
                ) as response:

                    # Domusa may return 440 instead of 401 when the token/session
                    # is expired. In either case, obtain a fresh token and retry once.
                    if response.status in (401, 440):
                        print(
                            f"Authentication expired or invalid "
                            f"(HTTP {response.status}). Re-authenticating..."
                        )

                        self.token = await self.auth.get_token()

                        if not self.token:
                            print("ERROR: Could not obtain a new authentication token")
                            return None

                        retry_headers = {
                            "Authorization": f"Bearer {self.token}",
                            "Content-Type": "application/json",
                        }

                        async with session.request(
                            method,
                            url,
                            headers=retry_headers,
                            json=json_data,
                        ) as retry:

                            if 200 <= retry.status < 300:
                                try:
                                    return await retry.json()
                                except Exception:
                                    return True

                            print(
                                f"API error after authentication retry "
                                f"{method} {url}: HTTP {retry.status}"
                            )
                            return None

                    if 200 <= response.status < 300:
                        try:
                            return await response.json()
                        except Exception:
                            return True

                    print(f"API error {method} {url}: HTTP {response.status}")
                    return None

        except Exception as e:
            print(f"API Error at {url}: {e}")
            return None

    async def _get(self, url):
        result = await self._request("GET", url)
        return result if isinstance(result, (dict, list)) else {}

    async def get_calderas(self):
        """Return every Domusa installation/heat pump available to the account."""
        url = f"{self.base}/v1/usuario/calderas/aliases"
        data = await self._get(url)

        devices = []

        if isinstance(data, dict):
            for alias, value in data.items():
                if isinstance(value, dict):
                    cid = value.get("idcaldera", alias)
                    name = (
                        value.get("alias")
                        or value.get("nombre")
                        or value.get("name")
                        or str(alias)
                    )
                else:
                    cid = alias
                    name = str(alias)

                devices.append({
                    "id": str(cid),
                    "name": str(name),
                    "alias": str(alias),
                })

        elif isinstance(data, list):
            for index, value in enumerate(data):
                if not isinstance(value, dict):
                    continue

                cid = value.get("idcaldera") or value.get("id")

                if cid is None:
                    continue

                name = (
                    value.get("alias")
                    or value.get("nombre")
                    or value.get("name")
                    or f"Domusa {index + 1}"
                )

                devices.append({
                    "id": str(cid),
                    "name": str(name),
                    "alias": str(name),
                })

        # Remove accidental duplicates while preserving API order.
        unique = []
        seen = set()

        for device in devices:
            if device["id"] not in seen:
                seen.add(device["id"])
                unique.append(device)

        return unique

    async def get_caldera(self):
        """Backward-compatible helper: returns the first device."""
        devices = await self.get_calderas()
        return devices[0] if devices else None

    async def get_estado(self, cid):
        return await self._get(
            f"{self.base}/v2/calderas/{cid}/estado"
        )

    async def get_config(self, cid):
        return await self._get(
            f"{self.base}/v2/calderas/{cid}/configuracion"
        )

    async def set_acs(self, cid, temperature):
        url = f"{self.base}/v2/calderas/{cid}/estado"
        return await self._request(
            "PUT",
            url,
            {"st_acs_p04": int(temperature)},
        )
