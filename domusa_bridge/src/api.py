import aiohttp


class DomusaAPI:
    def __init__(self, auth):
        self.base = "https://ic-api-app.azurewebsites.net/api"
        self.auth = auth
        self.token = None

    async def _get_headers(self):
        if not self.token:
            self.token = await self.auth.get_token()
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def _request(self, method, url, json_data=None):
        headers = await self._get_headers()
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.request(method, url, json=json_data, timeout=10) as response:
                    if response.status == 401:
                        self.token = await self.auth.get_token()
                        headers["Authorization"] = f"Bearer {self.token}"
                        async with session.request(method, url, json=json_data, timeout=10) as retry:
                            if retry.status == 200:
                                try:
                                    return await retry.json()
                                except Exception:
                                    return True
                            print(f"API error {method} {url}: HTTP {retry.status}")
                            return None

                    if response.status == 200:
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

                devices.append({"id": str(cid), "name": str(name), "alias": str(alias)})
        elif isinstance(data, list):
            for index, value in enumerate(data):
                if not isinstance(value, dict):
                    continue
                cid = value.get("idcaldera") or value.get("id")
                if cid is None:
                    continue
                name = value.get("alias") or value.get("nombre") or value.get("name") or f"Domusa {index + 1}"
                devices.append({"id": str(cid), "name": str(name), "alias": str(name)})

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
        return await self._get(f"{self.base}/v2/calderas/{cid}/estado")

    async def get_config(self, cid):
        return await self._get(f"{self.base}/v2/calderas/{cid}/configuracion")

    async def set_acs(self, cid, temperature):
        url = f"{self.base}/v2/calderas/{cid}/estado"
        return await self._request("PUT", url, {"st_acs_p04": int(temperature)})

    async def set_config_value(self, cid, key, value):
        """Update a writable Domusa configuration parameter."""
        url = f"{self.base}/v2/calderas/{cid}/configuracion"
        return await self._request("PUT", url, {key: value})

    async def set_otc_curve(self, cid, curve):
        # Zone 1 OTC curve (P154). Only these discrete values are supported by Domusa.
        allowed_curves = {6.0, 5.0, 4.0, 3.0, 2.5, 2.0, 1.5, 1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2}
        curve = round(float(curve), 1)
        if curve not in allowed_curves:
            raise ValueError(
                f"Unsupported OTC curve {curve}. Allowed values: "
                "6, 5, 4, 3, 2.5, 2, 1.5, 1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2"
            )
        return await self.set_config_value(cid, "ck_zona1_p154", curve)
