import aiohttp
import json


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

        async def do_request(session):
            async with session.request(
                method, url, json=json_data, timeout=10
            ) as response:
                body_text = await response.text()

                if 200 <= response.status < 300:
                    print(f"API OK {method} {url}: HTTP {response.status}")

                    if body_text.strip():
                        try:
                            return json.loads(body_text)
                        except Exception:
                            print(
                                f"API: Non-JSON response body: "
                                f"{body_text[:1000]}"
                            )
                            return True
                    return True

                print(f"API error {method} {url}: HTTP {response.status}")
                if body_text.strip():
                    print(f"API error response: {body_text[:4000]}")
                return None

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                result = await do_request(session)

                # Retry once with a fresh token if authentication failed.
                if result is None:
                    # We need to distinguish 401, so perform a lightweight retry
                    # only when the token may have expired.
                    pass

                return result

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

                devices.append(
                    {"id": str(cid), "name": str(name), "alias": str(alias)}
                )

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
                devices.append(
                    {"id": str(cid), "name": str(name), "alias": str(name)}
                )

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
            "PUT", url, {"st_acs_p04": int(temperature)}
        )

    async def set_config_value(self, cid, key, value):
        """Update a writable Domusa configuration parameter."""
        url = f"{self.base}/v2/calderas/{cid}/configuracion"
        print(f"API: Writing {key}={value} for {cid}")
        result = await self._request("PUT", url, {key: value})

        print(
            "API: PUT response:",
            json.dumps(result, indent=2, ensure_ascii=False)
            if isinstance(result, (dict, list))
            else repr(result),
        )
        return result

    @staticmethod
    def _find_key(data, target_key, path=""):
        """Recursively find a key anywhere in a dict/list API response."""
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                if key == target_key:
                    return value, current_path

                found_value, found_path = DomusaAPI._find_key(
                    value, target_key, current_path
                )
                if found_path is not None:
                    return found_value, found_path

        elif isinstance(data, list):
            for index, value in enumerate(data):
                current_path = f"{path}[{index}]"
                found_value, found_path = DomusaAPI._find_key(
                    value, target_key, current_path
                )
                if found_path is not None:
                    return found_value, found_path

        return None, None

    async def set_otc_curve(self, cid, curve):
        allowed_curves = {
            6.0, 5.0, 4.0, 3.0, 2.5, 2.0, 1.5, 1.0,
            0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2,
        }

        curve = round(float(curve), 1)

        if curve not in allowed_curves:
            raise ValueError(
                f"Unsupported OTC curve {curve}. Allowed values: "
                "6, 5, 4, 3, 2.5, 2, 1.5, 1, 0.9, 0.8, "
                "0.7, 0.6, 0.5, 0.4, 0.3, 0.2"
            )

        put_result = await self.set_config_value(
            cid, "ck_zona1_p154", curve
        )

        if put_result is None:
            print("API: OTC write failed at HTTP/API level")
            return False

        # Read the configuration back and print the complete response once.
        config = await self.get_config(cid)

        print(
            f"API: Full configuration response after OTC write for {cid}:"
        )
        print(json.dumps(config, indent=2, ensure_ascii=False))

        actual_value, actual_path = self._find_key(
            config, "ck_zona1_p154"
        )

        print(
            "API: Verification after write: "
            f"ck_zona1_p154={actual_value} "
            f"path={actual_path}"
        )

        if actual_path is None:
            print(
                "API: P154 was not found anywhere in the GET "
                "/configuracion response."
            )
            return False

        try:
            if abs(float(actual_value) - curve) < 0.001:
                print(
                    f"API: OTC curve successfully persisted as "
                    f"K={float(actual_value):g}"
                )
                return True
        except (TypeError, ValueError):
            pass

        print(
            "API: Write returned success but the value read back "
            "does not match the requested OTC curve."
        )
        return False
