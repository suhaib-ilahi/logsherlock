# LogSherlock

LogSherlock is an interactive CLI-based log investigation and debugging tool for analyzing mixed-format server logs.

It is designed for operational debugging and incident investigation of server log files.

The tool handles:

- Standard plaintext web server logs
- Mixed timestamp formats
- JSON-formatted log lines
- Missing status codes
- Different response time units
- Extra appended fields (user agents, referrers, etc.)
- Malformed and inconsistent log lines

LogSherlock preserves anomalies with line numbers and parser failure reasons for easier debugging.

---

## Commands:

- `report` → overall summary report
- `slowest` → top slow endpoints
- `errors` → all 4xx / 5xx logs
- `anomalies` → malformed / inconsistent logs
- `endpoint <path>` → inspect endpoint activity
- `ip <address>` → trace requests by IP
- `status <code>` → query logs by status code
- `method <HTTP_METHOD>` → query by HTTP method
- `search <query>` → raw text log search
- `next` / `prev` → move between large results
- `help` → list all the commands
- `exit` →  exit the REPL environment

---

## Installation

### Clone repository

```bash
git clone <your-repo-url>
cd log-analyzer
```

### Install dependencies

```bash
pip install .
```

This installs:

- python-dateutil
- rich

---

## Running the tool

```bash
logsherlock
```

---

## Example Usage

Start:

```bash

logsherlock

```

Load file:

```text
Enter log file path: sample_logs/generated.log
```

Interactive shell:

```text
LogSherlock> report
LogSherlock> slowest
LogSherlock> status 500
LogSherlock> method POST
LogSherlock> ip 192.168.1.42
LogSherlock> endpoint /api/users
LogSherlock> search login
LogSherlock> anomalies
LogSherlock> next
LogSherlock> prev
LogSherlock> exit
```

---

## Generating Test Data

A synthetic log generator is included.

Generate representative logs:

```bash
python scripts/generate_logs.py
```

This creates:

```text
sample_logs/generated.log
```

Generated logs include:

- standard logs
- JSON logs
- malformed lines
- missing status codes
- multiple timestamp formats
- extra appended fields
- varied response time units

---

## Project Structure

```text
log-analyzer/
│
├── logsherlock/
│   ├── __init__.py
│   ├── __main__.py
│   ├── analyzer.py
│   ├── parser.py
│   ├── repository.py
│   ├── metrics.py
│   └── ui.py
│
├── scripts/
│   └── generate_logs.py
│
├── sample_logs/
├── README.md
├── ANSWERS.md
├── pyproject.toml
```

---

## Design Notes

Architecture is separated by responsibility:

- **parser.py** → parsing + validation + anomaly classification
- **repository.py** → in-memory indexed datastore
- **metrics.py** → analytics and summary generation
- **ui.py** → Rich terminal UI + pagination
- **analyzer.py** → interactive CLI controller

Logs are parsed once and indexed in memory for efficient repeated querying.

---

## Supported Input Variations

Examples handled:

Plain:

```text
2024-03-15T14:23:01Z 192.168.1.42 GET /api/users 200 142ms
```

Alternative timestamps:

```text
2024/03/15 14:23:01
15-Mar-2024 14:23:01
1710512581
```

JSON:

```json
{"timestamp":"2024-03-15T14:23:01Z","ip":"1.2.3.4","method":"GET","path":"/api","status":200,"response_time":"142ms"}
```

Malformed:

```text
Exception in thread main
partial write 192.168
```

---