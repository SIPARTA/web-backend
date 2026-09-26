from datetime import datetime, timezone, timedelta

def test_logic(devices):
    now = datetime.now(timezone.utc)
    is_online = False
    for dev in devices:
        last_seen_str = dev.get("last_seen")
        if last_seen_str:
            try:
                last_seen_dt = datetime.fromisoformat(last_seen_str.replace("Z", "+00:00"))
                diff = now - last_seen_dt
                if timedelta(seconds=-60) < diff < timedelta(seconds=60):
                    is_online = True
                    break
            except Exception as e:
                print(e)
    return is_online

print("Empty array:", test_logic([]))
print("Old timestamp:", test_logic([{"last_seen": "2023-01-01T00:00:00Z"}]))
print("Future timestamp (invalid):", test_logic([{"last_seen": "2030-01-01T00:00:00Z"}]))
print("Recent timestamp:", test_logic([{"last_seen": (datetime.now(timezone.utc) - timedelta(seconds=10)).isoformat()}]))
