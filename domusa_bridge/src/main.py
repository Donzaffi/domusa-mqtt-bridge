import sys
print("DEBUG: Skript wurde gestartet!")
sys.stdout.flush()

try:
    print("DEBUG: Versuche Module zu importieren...")
    import asyncio
    print("DEBUG: asyncio geladen.")
    
    # Hier simulieren wir nur einen Start ohne API/MQTT
    print("DEBUG: Starte Event Loop...")
    async def minimal():
        print("DEBUG: Innerhalb von async!")
        await asyncio.sleep(1)
        print("DEBUG: Beende minimal.")
        
    asyncio.run(minimal())
    print("DEBUG: Skript beendet.")
except Exception as e:
    print(f"DEBUG: FEHLER beim Start: {e}")
