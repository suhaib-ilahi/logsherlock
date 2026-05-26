from collections import Counter, defaultdict

class LogMetrics:
    def __init__(self):
        self.total_lines = 0
        self.valid_lines = 0
        self.malformed_lines = 0

        self.status_counts = Counter()
        self.endpoint_counts = Counter()
        self.ip_counts = Counter()
        self.method_counts = Counter()
        self.format_counts = Counter()

        self.missing_status = 0

        self.endpoint_response = defaultdict(
            lambda: {"total": 0, "count": 0}
        )

    def mark_malformed(self):
        self.total_lines += 1
        self.malformed_lines += 1

    def consume(self, entry):
        self.total_lines += 1
        self.valid_lines += 1

        self.endpoint_counts[entry["path"]] += 1
        self.ip_counts[entry["ip"]] += 1
        self.method_counts[entry["method"]] += 1
        self.format_counts[entry["format_type"]] += 1

        if entry["status"] is None:
            self.missing_status += 1
        else:
            self.status_counts[entry["status"]] += 1

        endpoint = self.endpoint_response[entry["path"]]
        endpoint["total"] += entry["response_time_ms"]
        endpoint["count"] += 1

    def get_error_summary(self):
        client_errors = 0
        server_errors = 0

        for status, count in self.status_counts.items():
            if 400 <= status < 500:
                client_errors += count
            elif 500 <= status < 600:
                server_errors += count

        return client_errors, server_errors


    def get_slowest_endpoints(self, limit=10):
        averages = []

        for endpoint, data in self.endpoint_response.items():
            avg = data["total"] / data["count"]
            averages.append((endpoint, avg))

        averages.sort(key=lambda x: x[1], reverse=True)

        return averages[:limit]
    
    def report(self):
        client_errors, server_errors = self.get_error_summary()

        print("\n===== LOG ANALYSIS REPORT =====\n")

        print(f"Total lines processed: {self.total_lines}")
        print(f"Valid lines parsed: {self.valid_lines}")
        print(f"Malformed/skipped lines: {self.malformed_lines}")
        print(f"Missing status entries: {self.missing_status}")

        print("\nFormat distribution:")
        for fmt, count in self.format_counts.items():
            print(f"  {fmt}: {count}")

        print("\nHTTP methods:")
        for method, count in self.method_counts.most_common():
            print(f"  {method}: {count}")

        print("\nStatus code distribution:")
        for status, count in self.status_counts.most_common():
            print(f"  {status}: {count}")

        print(f"\n4xx errors: {client_errors}")
        print(f"5xx errors: {server_errors}")

        print("\nTop 10 endpoints:")
        for endpoint, count in self.endpoint_counts.most_common(10):
            print(f"  {endpoint}: {count}")

        print("\nTop 10 IPs:")
        for ip, count in self.ip_counts.most_common(10):
            print(f"  {ip}: {count}")

        print("\nTop 10 slowest endpoints (avg ms):")
        for endpoint, avg in self.get_slowest_endpoints():
            print(f"  {endpoint}: {avg:.2f} ms")