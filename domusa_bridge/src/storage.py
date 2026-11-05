import json
import os


class Storage:
    DEVICE_FILE = "/data/device.json"
    DEVICES_FILE = "/data/devices.json"

    async def get_devices(self):
        # New multi-device storage.
        if os.path.exists(self.DEVICES_FILE):
            try:
                with open(self.DEVICES_FILE) as f:
                    devices = json.load(f)
                if isinstance(devices, list):
                    return devices
            except Exception as e:
                print(f"Storage error reading devices: {e}")

        # Migrate the old single-device cache if it exists.
        if os.path.exists(self.DEVICE_FILE):
            try:
                with open(self.DEVICE_FILE) as f:
                    device = json.load(f)
                if isinstance(device, dict) and device.get("id"):
                    return [device]
            except Exception as e:
                print(f"Storage error reading legacy device: {e}")
        return None

    async def save_devices(self, devices):
        with open(self.DEVICES_FILE, "w") as f:
            json.dump(devices, f, indent=2)

    async def get_device(self):
        devices = await self.get_devices()
        return devices[0] if devices else None

    async def save_device(self, device):
        await self.save_devices([device])
