import aiohttp

BASE_URL = "https://task1.interview.yavlenie.pro"

async def validate_account(account_number):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/meters/{account_number}") as resp:
            return resp.status == 200

async def validate_serial(serial_number):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/meter-info/{serial_number}") as resp:
            return resp.status == 200

async def submit_reading(serial_number, reading):
    payload = {
        "serialNumber": serial_number,
        "newReading": reading
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/submit-reading", json=payload) as resp:
            return resp.status == 200
