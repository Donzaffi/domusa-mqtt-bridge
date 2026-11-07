import asyncio
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
        url = f"{self.base}/v1/usuario/calderas/aliases"
        data = await self._get(url)

        devices = []
        if isinstance(data, dict):
            for alias, value in data.items():
                if isinstance(value, dict):
                    cid = value.get("idcaldera", alias)
                    name = value.get("alias") or value.get("nombre") or value.get("name") or str(alias)
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

        unique = []
        seen = set()
        for device in devices:
            if device["id"] not in seen:
                seen.add(device["id"])
                unique.append(device)
        return unique

    async def get_caldera(self):
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
        url = f"{self.base}/v2/calderas/{cid}/configuracion"
        return await self._request("PUT", url, {key: value})

    async def set_otc_curve(self, cid, curve):
        # Zone 1 OTC curve (P154). 0 means OFF.
        allowed_curves = {
            0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,
            1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0,
        }

        curve = round(float(curve), 1)
        if curve not in allowed_curves:
            raise ValueError(
                f"Unsupported OTC curve {curve}. Allowed values: "
                "0 (Off), 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, "
                "1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0"
            )

        print(f"API: Writing ck_zona1_p154={curve} for {cid}")
        result = await self.set_config_value(cid, "ck_zona1_p154", curve)

        # A successful PUT does not always echo updatedData.ck_zona1_p154.
        # Therefore, accept a valid API response and verify by reading the
        # configuration back from the server.
        if result is None:
            print("API: OTC curve write request failed")
            return False

        if isinstance(result, dict):
            updated = result.get("updatedData")
            if isinstance(updated, dict) and "ck_zona1_p154" in updated:
                persisted = updated["ck_zona1_p154"]
                print(f"API: Verification from updatedData: ck_zona1_p154={persisted}")
                try:
                    if round(float(persisted), 1) == curve:
                        return True
                except (TypeError, ValueError):
                    pass
            else:
                print("API: PUT successful; value not echoed in response, verifying with GET")
        else:
            # _request() can return True for a successful response without JSON.
            print("API: PUT successful; no JSON body, verifying with GET")

        # The cloud backend can apply configuration asynchronously. Retry a
        # few times before declaring the write unsuccessful.
        for attempt in range(1, 6):
            await asyncio.sleep(1)
            config = await self.get_config(cid)

            # Support either a flat config object or common nested wrappers.
            candidates = [config]
            if isinstance(config, dict):
                for wrapper in ("updatedData", "data", "configuracion", "config"):
                    nested = config.get(wrapper)
                    if isinstance(nested, dict):
                        candidates.append(nested)

            persisted = None
            for candidate in candidates:
                if isinstance(candidate, dict) and "ck_zona1_p154" in candidate:
                    persisted = candidate["ck_zona1_p154"]
                    break

            print(
                f"API: Verification attempt {attempt}/5: "
                f"ck_zona1_p154={persisted}"
            )

            try:
                if persisted is not None and round(float(persisted), 1) == curve:
                    print("API: OTC curve write confirmed by GET")
                    return True
            except (TypeError, ValueError):
                pass

        print("API: OTC curve write was not confirmed after GET verification")
        return False

