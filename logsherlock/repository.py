from collections import defaultdict
from logsherlock.parser import parse_line


class LogRepository:
    def __init__(self):
        self.entries = []
        self.malformed_lines = []

        self.by_ip = defaultdict(list)
        self.by_endpoint = defaultdict(list)
        self.by_status = defaultdict(list)
        self.by_method = defaultdict(list)

        self.total_lines = 0

    def add_entry(self, entry):
        self.entries.append(entry)

        self.by_ip[entry["ip"]].append(entry)
        self.by_endpoint[entry["path"]].append(entry)
        self.by_method[entry["method"]].append(entry)

        if entry["status"] is not None:
            self.by_status[entry["status"]].append(entry)

    def add_malformed(self, line_number, raw_line, reason):
        self.malformed_lines.append({
            "line_number": line_number,
            "raw_line": raw_line,
            "reason": reason
        })

    def load(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                self.total_lines += 1

                raw_line = line.rstrip("\n")

                result = parse_line(raw_line)

                if result["success"]:
                    entry = result["entry"]
                    entry["line_number"] = line_number
                    self.add_entry(entry)

                else:
                    self.add_malformed(
                        line_number,
                        raw_line,
                        result["reason"]
                    )

    def get_status_entries(self, status_code):
        return self.by_status.get(status_code, [])

    def get_ip_entries(self, ip):
        return self.by_ip.get(ip, [])

    def get_endpoint_entries(self, endpoint):
        return self.by_endpoint.get(endpoint, [])

    def get_method_entries(self, method):
        return self.by_method.get(method.upper(), [])

    def search_raw(self, query):
        matches = []

        query = query.lower()

        for entry in self.entries:
            if query in entry["raw_line"].lower():
                matches.append(entry)

        for item in self.malformed_lines:
            if query in item["raw_line"].lower():
                matches.append(item)

        return matches