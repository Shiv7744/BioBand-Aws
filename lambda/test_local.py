from store_reading import lambda_handler

# A fake sample reading, just like your simulator generates
fake_event = {
    "device_id": "bioband-001",
    "timestamp": "2026-07-15T15:30:00+00:00",
    "heart_rate": 75,
    "spo2": 98,
    "temperature": 98.6
}

result = lambda_handler(fake_event, None)
print(result)