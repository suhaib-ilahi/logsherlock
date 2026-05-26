from collections import defaultdict
from parser import parse_line


class LogRepository:
    def __init__(self):
        self.entries = []
        self.malformed_lines = []

        self.by_ip = defaultdict(list)
        self.by_endpoint = defaultdict(list)
        self.by_status = defaultdict(list)
        self.by_method = defaultdict(list)

    def load(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                raw_line = line.rstrip("\n")

                entry = parse_line(raw_line)

                if entry is None:
                    if raw_line.strip():
                        self.malformed_lines.append({
                            "line_number": line_number,
                            "raw_line": raw_line,
                            "reason": "Failed parser validation"
                        })
                    continue

                entry["raw_line"] = raw_line
                entry["line_number"] = line_number

                self.entries.append(entry)

                self.by_ip[entry["ip"]].append(entry)
                self.by_endpoint[entry["path"]].append(entry)
                self.by_method[entry["method"]].append(entry)

                if entry["status"] is not None:
                    self.by_status[entry["status"]].append(entry)