# ANSWERS

## 1. How to run

Clone repository:

```bash
git clone <your-repo-url>
cd log-analyzer
```

Install:

```bash
pip install .
```

Generate sample logs (optional):

```bash
python scripts/generate_logs.py
```

Run (If PATH is NOT configured):

```bash
python -m logsherlock
```

Else Run:

```bash
logsherlock
```

---

## 2. Stack choice

I chose Python because this task is primarily a text parsing, normalization, and data querying problem.

Python provides:

- library support for text processing
- JSON parsing
- regular expressions
- datetime handling
- clean CLI tooling

I used:

- **python-dateutil** for  timestamp parsing
- **rich** for terminal UX and pagination rendering

I intentionally chose an interactive CLI instead of a web dashboard because the assignment emphasizes robustness against unknown inputs and operational usefulness rather than frontend polish.

A worse choice would have been a browser-only frontend implementation because:

- parsing very large files client-side is inefficient
- debugging workflows are naturally CLI-oriented
- handling malformed mixed-format logs becomes unnecessarily complex in browser-only environments

A heavy backend framework like Django or Spring Boot would also be overkill for this problem.

---

## 3. One real edge case

Edge case: malformed lines containing useful debugging evidence.

Example:

```text
partial write 192.168.1.42 GET ????
```

Even though this line fails structured parsing, the IP may still be useful during incident investigation.

Handled in:

```text
logsherlock/repository.py
```

Specifically in malformed line storage and raw search fallback logic.

Without this handling, malformed evidence would be silently discarded and users tracing an IP or endpoint would miss relevant information.

Instead, LogSherlock preserves:

- raw malformed line
- original line number
- parser failure reason

This improves debugging transparency.

---

## 4. AI usage

I used ChatGPT during development for architectural brainstorming, parser design validation, CLI UX refinement, packaging guidance, and documentation drafting.

Specific uses:

- parser architecture design
- repository/indexing architecture
- interactive shell design
- packaging (`pyproject.toml`, entry points)
- README/ANSWERS drafting

One notable change I made to AI-generated ideas:

Initially, a simpler static report generator architecture was considered. I changed the design into an interactive CLI investigation tool with indexed in-memory querying, anomaly preservation, pagination, and rich terminal UI because that better matched operational debugging workflows.

I also rejected an earlier temporary-file caching approach in favor of an in-memory repository abstraction, which is cleaner and more efficient for this problem scale.

---

## 5. Honest gap

One limitation is that LogSherlock currently keeps parsed data in memory for the active session.

This is efficient for the assignment scale (hundreds to hundreds of thousands of lines), but repeated loading of very large multi-GB log files would be slower than a persistent indexed cache.

With another day, I would implement:

- persistent on-disk caching (SQLite or indexed JSONL)
- timestamp range filtering
- parser plugin support for custom log formats
- export functionality for filtered investigations