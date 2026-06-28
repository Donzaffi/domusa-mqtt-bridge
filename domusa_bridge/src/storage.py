import json
import os


class Storage:
    DEVICE_FILE = "/data/device.json"

    async def get_device(self):
        if not os.path.exists(self.DEVICE_FILE):
            return None

        with open(self.DEVICE_FILE) as f:
            return json.load(f)

    async def save_device(self, device):
        with open(self.DEVICE_FILE, "w") as f:
            json.dump(device, f)
