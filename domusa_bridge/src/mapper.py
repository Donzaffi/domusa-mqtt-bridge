def map_state(data):
    return {
        "temperature": data.get("temperature"),
        "power": data.get("power"),
        "mode": data.get("mode")
    }
