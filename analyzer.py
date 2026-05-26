import argparse
import sys

from repository import LogRepository
from metrics import LogMetrics


def load_repository(file_path):
    repo = LogRepository()

    try:
        repo.load(file_path)
    except FileNotFoundError:
        print(f"Error: File not found -> {file_path}")
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied -> {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

    return repo


def command_report(repo):
    metrics = LogMetrics()

    for entry in repo.entries:
        metrics.consume(entry)

    for malformed in repo.malformed_lines:
        metrics.mark_malformed()

    metrics.report()


def command_slowest(repo):
    endpoint_stats = {}

    for entry in repo.entries:
        path = entry["path"]

        if path not in endpoint_stats:
            endpoint_stats[path] = {"total": 0, "count": 0}

        endpoint_stats[path]["total"] += entry["response_time_ms"]
        endpoint_stats[path]["count"] += 1

    averages = []

    for endpoint, data in endpoint_stats.items():
        avg = data["total"] / data["count"]
        averages.append((endpoint, avg))

    averages.sort(key=lambda x: x[1], reverse=True)

    print("\n===== TOP 10 SLOWEST ENDPOINTS =====\n")

    for endpoint, avg in averages[:10]:
        print(f"{endpoint:<30} {avg:.2f} ms")


def command_errors(repo):
    print("\n===== ERROR LOGS (4xx / 5xx) =====\n")

    found = False

    for entry in repo.entries:
        status = entry["status"]

        if status is not None and 400 <= status < 600:
            print(entry["raw_line"])
            found = True

    if not found:
        print("No error logs found.")


def command_anomalies(repo):
    print("\n===== MALFORMED / ANOMALOUS LOGS =====\n")

    if not repo.malformed_lines:
        print("No malformed logs found.")
        return

    for line in repo.malformed_lines[:50]:
        print(
            f"Line {item['line_number']}: "
            f"{item['raw_line']}"
        )
        print(f"Reason: {item['reason']}\n")

    if len(repo.malformed_lines) > 50:
        print(f"\n... and {len(repo.malformed_lines) - 50} more")


def command_endpoint(repo, endpoint):
    entries = repo.by_endpoint.get(endpoint, [])

    print(f"\n===== ENDPOINT ANALYSIS: {endpoint} =====\n")

    if not entries:
        print("No matching logs found.")
        return

    total = len(entries)
    avg = sum(e["response_time_ms"] for e in entries) / total

    print(f"Total requests: {total}")
    print(f"Average response time: {avg:.2f} ms\n")

    print("Recent logs:\n")

    for entry in entries[-20:]:
        print(entry["raw_line"])


def command_ip(repo, ip):
    entries = repo.by_ip.get(ip, [])

    print(f"\n===== IP TRACE: {ip} =====\n")

    if entries:
        print("VALID PARSED ENTRIES:\n")

        for entry in entries[-50:]:
            print(f"Line {entry['line_number']}: {entry['raw_line']}")

    malformed_matches = []

    for item in repo.malformed_lines:
        if ip in item["raw_line"]:
            malformed_matches.append(item)

    if malformed_matches:
        print("\nMALFORMED / INCONSISTENT MATCHES:\n")

        for item in malformed_matches[:20]:
            print(
                f"Line {item['line_number']}: "
                f"{item['raw_line']}"
            )
            print(f"Reason: {item['reason']}\n")

    if not entries and not malformed_matches:
        print("No matching logs found.")

def main():
    parser = argparse.ArgumentParser(
        description="Log Analyzer CLI"
    )

    subparsers = parser.add_subparsers(dest="command")

    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("file")

    slowest_parser = subparsers.add_parser("slowest")
    slowest_parser.add_argument("file")

    errors_parser = subparsers.add_parser("errors")
    errors_parser.add_argument("file")

    anomalies_parser = subparsers.add_parser("anomalies")
    anomalies_parser.add_argument("file")

    endpoint_parser = subparsers.add_parser("endpoint")
    endpoint_parser.add_argument("file")
    endpoint_parser.add_argument("endpoint")

    ip_parser = subparsers.add_parser("ip")
    ip_parser.add_argument("file")
    ip_parser.add_argument("ip")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    repo = load_repository(args.file)

    if args.command == "report":
        command_report(repo)

    elif args.command == "slowest":
        command_slowest(repo)

    elif args.command == "errors":
        command_errors(repo)

    elif args.command == "anomalies":
        command_anomalies(repo)

    elif args.command == "endpoint":
        command_endpoint(repo, args.endpoint)

    elif args.command == "ip":
        command_ip(repo, args.ip)


if __name__ == "__main__":
    main()