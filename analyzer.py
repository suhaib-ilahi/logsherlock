import sys

from repository import LogRepository
from metrics import LogMetrics
from ui import (
    Paginator,
    show_banner,
    show_help,
    print_message,
    console
)


def load_repository():
    file_path = input("Enter log file path: ").strip()

    if not file_path:
        print_message("No file path provided.", "red")
        sys.exit(1)

    repo = LogRepository()

    try:
        repo.load(file_path)

    except FileNotFoundError:
        print_message(
            f"File not found: {file_path}",
            "red"
        )
        sys.exit(1)

    except PermissionError:
        print_message(
            f"Permission denied: {file_path}",
            "red"
        )
        sys.exit(1)

    except Exception as e:
        print_message(
            f"Unexpected error: {e}",
            "red"
        )
        sys.exit(1)

    show_banner(repo)

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
            endpoint_stats[path] = {
                "total": 0,
                "count": 0
            }

        endpoint_stats[path]["total"] += entry["response_time_ms"]
        endpoint_stats[path]["count"] += 1

    rows = []

    for endpoint, data in endpoint_stats.items():
        avg = data["total"] / data["count"]

        rows.append({
            "line_number": "-",
            "raw_line": f"{endpoint} | {avg:.2f} ms"
        })

    rows.sort(
        key=lambda x: float(
            x["raw_line"].split("|")[1]
            .replace("ms", "")
            .strip()
        ),
        reverse=True
    )

    return rows


def command_errors(repo):
    results = []

    for entry in repo.entries:
        status = entry["status"]

        if status is not None and 400 <= status < 600:
            results.append(entry)

    return results


def command_anomalies(repo):
    return repo.malformed_lines


def command_endpoint(repo, endpoint):
    results = []

    results.extend(repo.get_endpoint_entries(endpoint))

    for item in repo.malformed_lines:
        if endpoint in item["raw_line"]:
            results.append(item)

    return results


def command_ip(repo, ip):
    results = []

    results.extend(repo.get_ip_entries(ip))

    for item in repo.malformed_lines:
        if ip in item["raw_line"]:
            results.append(item)

    return results


def command_status(repo, code):
    try:
        code = int(code)
    except ValueError:
        print_message("Invalid status code.", "red")
        return []

    return repo.get_status_entries(code)


def command_method(repo, method):
    return repo.get_method_entries(method)


def command_search(repo, query):
    return repo.search_raw(query)


def shell(repo):
    paginator = Paginator()

    show_help()

    while True:
        try:
            command = input("\nloganalyzer> ").strip()

            if not command:
                continue

            if command == "exit":
                print_message("Exiting Log Analyzer.", "yellow")
                break

            elif command == "help":
                show_help()

            elif command == "report":
                command_report(repo)

            elif command == "slowest":
                paginator.set_results(
                    command_slowest(repo),
                    "Top Slowest Endpoints"
                )
                paginator.render()

            elif command == "errors":
                paginator.set_results(
                    command_errors(repo),
                    "Error Logs"
                )
                paginator.render()

            elif command == "anomalies":
                paginator.set_results(
                    command_anomalies(repo),
                    "Malformed Logs"
                )
                paginator.render()

            elif command.startswith("endpoint "):
                endpoint = command[len("endpoint "):].strip()

                paginator.set_results(
                    command_endpoint(repo, endpoint),
                    f"Endpoint: {endpoint}"
                )
                paginator.render()

            elif command.startswith("ip "):
                ip = command[len("ip "):].strip()

                paginator.set_results(
                    command_ip(repo, ip),
                    f"IP Trace: {ip}"
                )
                paginator.render()

            elif command.startswith("status "):
                code = command[len("status "):].strip()

                paginator.set_results(
                    command_status(repo, code),
                    f"Status {code}"
                )
                paginator.render()

            elif command.startswith("method "):
                method = command[len("method "):].strip()

                paginator.set_results(
                    command_method(repo, method),
                    f"Method {method}"
                )
                paginator.render()

            elif command.startswith("search "):
                query = command[len("search "):].strip()

                paginator.set_results(
                    command_search(repo, query),
                    f"Search: {query}"
                )
                paginator.render()

            elif command == "next":
                if paginator.next_page():
                    paginator.render()
                else:
                    print_message(
                        "Already at last page.",
                        "yellow"
                    )

            elif command == "prev":
                if paginator.prev_page():
                    paginator.render()
                else:
                    print_message(
                        "Already at first page.",
                        "yellow"
                    )

            else:
                print_message(
                    "Unknown command. Type help.",
                    "red"
                )

        except KeyboardInterrupt:
            print_message(
                "\nExiting Log Analyzer.",
                "yellow"
            )
            break


def main():
    repo = load_repository()
    shell(repo)


if __name__ == "__main__":
    main()