import re
import json
from datetime import datetime
from dateutil import parser as date_parser


HTTP_METHODS = {
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "PATCH",
    "OPTIONS",
    "HEAD"
}


IP_REGEX = re.compile(
    r"^(?:\d{1,3}\.){3}\d{1,3}$"
)


def success(entry):
    return {
        "success": True,
        "entry": entry
    }


def failure(reason):
    return {
        "success": False,
        "reason": reason
    }


def parse_timestamp(ts):
    ts = ts.strip()

    if not ts:
        return None

    if ts.isdigit():
        try:
            return datetime.fromtimestamp(int(ts))
        except (ValueError, OverflowError, OSError):
            return None

    formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y/%m/%d %H:%M:%S",
        "%d-%b-%Y %H:%M:%S"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(ts, fmt)
        except ValueError:
            continue

    try:
        return date_parser.parse(ts)
    except Exception:
        return None


def parse_response_time(rt):
    rt = rt.strip().lower()

    try:
        if rt.endswith("ms"):
            return int(float(rt[:-2]))

        if rt.endswith("s"):
            return int(float(rt[:-1]) * 1000)

        return int(float(rt))

    except ValueError:
        return None


def extract_timestamp(parts):
    if not parts:
        return None, 0

    ts = parse_timestamp(parts[0])
    if ts:
        return ts, 1

    if len(parts) >= 2:
        combined = parts[0] + " " + parts[1]
        ts = parse_timestamp(combined)

        if ts:
            return ts, 2

    return None, 0


def parse_json_line(line):
    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        return failure("Malformed JSON")

    timestamp = parse_timestamp(str(data.get("timestamp", "")))

    if not timestamp:
        return failure("Invalid timestamp")

    ip = str(data.get("ip", ""))

    if not IP_REGEX.match(ip):
        return failure("Invalid IP")

    method = str(data.get("method", "")).upper()

    if method not in HTTP_METHODS:
        return failure("Unknown HTTP method")

    path = data.get("path")

    if not path:
        return failure("Missing path")

    response_time = parse_response_time(
        str(data.get("response_time", ""))
    )

    if response_time is None:
        return failure("Invalid response time")

    status = data.get("status")

    if status == "-":
        status = None
    elif status is not None:
        try:
            status = int(status)
        except ValueError:
            status = None

    return success({
        "timestamp": timestamp,
        "ip": ip,
        "method": method,
        "path": path,
        "status": status,
        "response_time_ms": response_time,
        "format_type": "json",
        "raw_line": line.strip()
    })


def parse_plain_line(line):
    line = line.strip()

    if not line:
        return failure("Blank line")

    parts = line.split()

    timestamp, consumed = extract_timestamp(parts)

    if not timestamp:
        return failure("Invalid timestamp")

    remaining = parts[consumed:]

    if len(remaining) < 5:
        return failure("Missing required fields")

    ip = remaining[0]

    if not IP_REGEX.match(ip):
        return failure("Invalid IP")

    method = remaining[1]

    if method not in HTTP_METHODS:
        return failure("Unknown HTTP method")

    path = remaining[2]
    status = remaining[3]
    response = remaining[4]

    if status == "-":
        status = None
    else:
        try:
            status = int(status)
        except ValueError:
            status = None

    response_time = parse_response_time(response)

    if response_time is None:
        return failure("Invalid response time")

    return success({
        "timestamp": timestamp,
        "ip": ip,
        "method": method,
        "path": path,
        "status": status,
        "response_time_ms": response_time,
        "format_type": "plain",
        "raw_line": line
    })


def parse_line(line):
    stripped = line.strip()

    if not stripped:
        return failure("Blank line")

    if stripped.startswith("{"):
        return parse_json_line(stripped)

    return parse_plain_line(stripped)