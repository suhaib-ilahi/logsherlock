import sys

from repository import LogRepository
from metrics import LogMetrics


def load_repository():
    file_path = input("Enter log file path: ").strip()

    if not file_path:
        print("No file path provided.")
        sys.exit(1)

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

    print("\nLog file loaded successfully.")
    print(f"Valid entries: {len(repo.entries)}")
    print(f"Malformed entries: {len(repo.malformed_lines)}")
    print("\nType 'help' for available commands.\n")

    return repo


def command_report(repo):
    metrics = LogMetrics()

    for entry in repo.entries:
        metrics.consume(entry)

    for _ in repo.malformed_lines:
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
            print(f"Line {entry['line_number']}: {entry['raw_line']}")
            found = True

    if not found:
        print("No error logs found.")


def command_anomalies(repo):
    print("\n===== MALFORMED / ANOMALOUS LOGS =====\n")

    if not repo.malformed_lines:
        print("No malformed logs found.")
        return

    for item in repo.malformed_lines[:50]:
        print(f"Line {item['line_number']}: {item['raw_line']}")
        print(f"Reason: {item['reason']}\n")

    if len(repo.malformed_lines) > 50:
        print(f"... and {len(repo.malformed_lines) - 50} more")


def command_endpoint(repo, endpoint):
    entries = repo.by_endpoint.get(endpoint, [])

    print(f"\n===== ENDPOINT ANALYSIS: {endpoint} =====\n")

    if entries:
        total = len(entries)
        avg = sum(e["response_time_ms"] for e in entries) / total

        print(f"Total requests: {total}")
        print(f"Average response time: {avg:.2f} ms\n")

        print("Recent valid logs:\n")

        for entry in entries[-20:]:
            print(f"Line {entry['line_number']}: {entry['raw_line']}")

    malformed_matches = []

    for item in repo.malformed_lines:
        if endpoint in item["raw_line"]:
            malformed_matches.append(item)

    if malformed_matches:
        print("\nMalformed/inconsistent matches:\n")

        for item in malformed_matches[:20]:
            print(f"Line {item['line_number']}: {item['raw_line']}")
            print(f"Reason: {item['reason']}\n")

    if not entries and not malformed_matches:
        print("No matching logs found.")


def command_ip(repo, ip):
    entries = repo.by_ip.get(ip, [])

    print(f"\n===== IP TRACE: {ip} =====\n")

    if entries:
        print("Valid parsed entries:\n")

        for entry in entries[-50:]:
            print(f"Line {entry['line_number']}: {entry['raw_line']}")

    malformed_matches = []

    for item in repo.malformed_lines:
        if ip in item["raw_line"]:
            malformed_matches.append(item)

    if malformed_matches:
        print("\nMalformed/inconsistent matches:\n")

        for item in malformed_matches[:20]:
            print(f"Line {item['line_number']}: {item['raw_line']}")
            print(f"Reason: {item['reason']}\n")

    if not entries and not malformed_matches:
        print("No matching logs found.")


def show_help():
    print("""
Available commands:

report                Show overall summary report
slowest               Show top 10 slowest endpoints
errors                Show all 4xx / 5xx error logs
anomalies             Show malformed / inconsistent logs
endpoint <path>       Inspect endpoint activity
ip <address>          Trace activity by IP
help                  Show this help
exit                  Exit the tool
""")


def shell(repo):
    while True:
        try:
            command = input("loganalyzer> ").strip()

            if not command:
                continue

            if command == "exit":
                print("Exiting Log Analyzer.")
                break

            elif command == "help":
                show_help()

            elif command == "report":
                command_report(repo)

            elif command == "slowest":
                command_slowest(repo)

            elif command == "errors":
                command_errors(repo)

            elif command == "anomalies":
                command_anomalies(repo)

            elif command.startswith("endpoint "):
                endpoint = command[len("endpoint "):].strip()
                command_endpoint(repo, endpoint)

            elif command.startswith("ip "):
                ip = command[len("ip "):].strip()
                command_ip(repo, ip)

            else:
                print("Unknown command. Type 'help'.")

        except KeyboardInterrupt:
            print("\nExiting Log Analyzer.")
            break


def main():
    repo = load_repository()
    shell(repo)


if __name__ == "__main__":
    main()