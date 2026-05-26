import os
import json
import random
from datetime import datetime, timedelta, UTC

HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]
PATHS = [
    "/api/users",
    "/api/login",
    "/api/orders",
    "/api/products",
    "/health",
    "/api/users/12"
]
STATUS_CODES = [200, 201, 400, 401, 403, 404, 500, 502]


def random_ip():
    return ".".join(str(random.randint(1, 255)) for _ in range(4))


def random_timestamp():
    base = datetime.now(UTC) - timedelta(
        seconds=random.randint(0, 100000)
    )

    choice = random.choice(["iso", "slash", "month", "epoch"])

    if choice == "iso":
        return base.strftime("%Y-%m-%dT%H:%M:%SZ")

    if choice == "slash":
        return base.strftime("%Y/%m/%d %H:%M:%S")

    if choice == "month":
        return base.strftime("%d-%b-%Y %H:%M:%S")

    return str(int(base.timestamp()))


def random_response_time():
    ms = random.randint(10, 2000)
    choice = random.choice(["ms", "seconds", "raw"])

    if choice == "ms":
        return f"{ms}ms"

    if choice == "seconds":
        return f"{ms / 1000:.3f}s"

    return str(ms)


def normal_log():
    return (
        f"{random_timestamp()} "
        f"{random_ip()} "
        f"{random.choice(HTTP_METHODS)} "
        f"{random.choice(PATHS)} "
        f"{random.choice(STATUS_CODES)} "
        f"{random_response_time()}"
    )


def missing_status_log():
    return (
        f"{random_timestamp()} "
        f"{random_ip()} "
        f"{random.choice(HTTP_METHODS)} "
        f"{random.choice(PATHS)} "
        f"- "
        f"{random_response_time()}"
    )


def extra_fields_log():
    return (
        normal_log()
        + ' "Mozilla/5.0" "https://google.com"'
    )


def malformed_log():
    options = [
        "",
        "broken incomplete line",
        "Exception in thread main",
        "partial write 192.168"
    ]
    return random.choice(options)


def json_log():
    entry = {
        "timestamp": random_timestamp(),
        "ip": random_ip(),
        "method": random.choice(HTTP_METHODS),
        "path": random.choice(PATHS),
        "status": random.choice(STATUS_CODES),
        "response_time": random_response_time()
    }

    return json.dumps(entry)


def generate_logs(count=5000):
    os.makedirs("sample_logs", exist_ok=True)

    with open("sample_logs/generated.log", "w", encoding="utf-8") as f:
        for _ in range(count):
            roll = random.random()

            if roll < 0.70:
                line = normal_log()
            elif roll < 0.80:
                line = json_log()
            elif roll < 0.87:
                line = missing_status_log()
            elif roll < 0.94:
                line = extra_fields_log()
            else:
                line = malformed_log()

            f.write(line + "\n")

    print("Generated sample_logs/generated.log")


if __name__ == "__main__":
    generate_logs()