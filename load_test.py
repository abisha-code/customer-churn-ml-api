import asyncio
import time
import httpx

URL = "http://127.0.0.1:8000/api/v1/predict"
HEADERS = {"X-API-Key": "supersecretkey123"}
PAYLOAD = {
    "Tenure Months": 12, "Monthly Charges": 75.50, "Total Charges": 906.00,
    "Gender": "Female", "Senior Citizen": "No", "Partner": "Yes",
    "Dependents": "No", "Phone Service": "Yes", "Multiple Lines": "No",
    "Internet Service": "Fiber optic", "Online Security": "No",
    "Online Backup": "No", "Device Protection": "No", "Tech Support": "No",
    "Streaming TV": "Yes", "Streaming Movies": "Yes",
    "Contract": "Month-to-month", "Paperless Billing": "Yes",
    "Payment Method": "Electronic check",
}
N_REQUESTS = 100


async def send_one(client, i):
    start = time.perf_counter()
    try:
        resp = await client.post(URL, json=PAYLOAD, headers=HEADERS, timeout=10.0)
        return {"status": resp.status_code, "elapsed": time.perf_counter() - start}
    except Exception as e:
        return {"status": None, "elapsed": time.perf_counter() - start, "error": str(e)}


async def main():
    async with httpx.AsyncClient() as client:
        overall_start = time.perf_counter()
        results = await asyncio.gather(*[send_one(client, i) for i in range(N_REQUESTS)])
        overall_elapsed = time.perf_counter() - overall_start

    successes = [r for r in results if r["status"] == 200]
    failures = [r for r in results if r["status"] != 200]
    times = [r["elapsed"] for r in results]

    print(f"Total requests: {N_REQUESTS}")
    print(f"Total wall time: {overall_elapsed:.2f}s")
    print(f"Successes: {len(successes)}  Failures: {len(failures)}")
    print(f"Avg response time: {sum(times)/len(times)*1000:.1f} ms")
    print(f"Min: {min(times)*1000:.1f} ms  Max: {max(times)*1000:.1f} ms")


asyncio.run(main())
