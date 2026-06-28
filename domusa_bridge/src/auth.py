import aiohttp

class Auth:
    BASE = "https://ic-api-app.azurewebsites.net"

    def __init__(self, username, password):
        self.username = username
        self.password = password

    async def get_token(self):
        # Header setzen, damit die API uns als JSON-Client erkennt
        headers = {"Content-Type": "application/json"}
        
        # URL anpassen: Falls /v2/ nicht klappt, versuche /v1/ wieder, 
        # aber prüfe in den Logs genau, was bei 'DEBUG: URL' steht.
        url = f"{self.BASE}/v1/auth/login" 
        
        payload = {
            "username": self.username,
            "password": self.password,
            "langDevice": "de"
        }

        print(f"DEBUG: Versuche Login an {url}")
        
        async with aiohttp.ClientSession(headers=headers) as s:
            async with s.post(url, json=payload) as r:
                data = await r.json()
                print("LOGIN RESPONSE:", data)
                
                if r.status != 200:
                    print(f"Fehler: Server antwortete mit Status {r.status}")
                    return None

                # Sicherer Zugriff auf das Token
                # Prüfe im Log, ob 'content' existiert oder ob 'token' direkt oben liegt
                if "content" in data and "token" in data["content"]:
                    return data["content"]["token"]
                elif "token" in data:
                    return data["token"]
                else:
                    print("Fehler: Token-Struktur in der Antwort nicht gefunden.")
                    return None
