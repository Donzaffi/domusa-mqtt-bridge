async def get_caldera(self):
        r = await self.session.get(f"{self.base}/v1/usuario/calderas/aliases")
        # Hier sicherstellen, dass die Antwort erfolgreich war
        if r.status != 200:
            print(f"API Fehler: Status {r.status}")
            return None
            
        data = await r.json()
        print(f"DEBUG: API Alias Antwort: {data}")
        
        try:
            # Wenn data ein dict ist, extrahieren wir es wie bisher
            if isinstance(data, dict) and data:
                first_key = list(data.keys())[0]
                # Eventuell ist idcaldera gar nicht im Sub-Dict, sondern der Key selbst?
                # Schau im Debug-Log: Wenn first_key z.B. eine Nummer ist, dann ist das die ID!
                id_wert = data[first_key].get("idcaldera") 
                
                # Falls idcaldera nicht gefunden wurde, nimm den first_key selbst
                if id_wert is None:
                    id_wert = first_key
                    
                return {"id": id_wert}
            return None
        except Exception as e:
            print(f"Fehler beim Extrahieren der idcaldera: {e}")
            return None
