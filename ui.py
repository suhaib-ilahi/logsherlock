from rich.console import Console
from rich.table import Table
from rich.panel import Panel


console = Console()


class Paginator:
    def __init__(self, page_size=20):
        self.page_size = page_size
        self.results = []
        self.current_page = 0
        self.title = "Results"

    def set_results(self, results, title="Results"):
        self.results = results
        self.current_page = 0
        self.title = title

    def has_results(self):
        return len(self.results) > 0

    def total_pages(self):
        if not self.results:
            return 0

        return (
            len(self.results) + self.page_size - 1
        ) // self.page_size

    def get_page(self):
        start = self.current_page * self.page_size
        end = start + self.page_size
        return self.results[start:end]

    def next_page(self):
        if self.current_page + 1 < self.total_pages():
            self.current_page += 1
            return True
        return False

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            return True
        return False

    def render(self):
        if not self.results:
            console.print(
                "[yellow]No results to display.[/yellow]"
            )
            return

        table = Table(
            title=(
                f"{self.title} "
                f"(Page {self.current_page + 1}/"
                f"{self.total_pages()})"
            )
        )

        table.add_column("Line", style="cyan")
        table.add_column("Content", style="white")
        table.add_column("Reason", style="red")

        for item in self.get_page():
            if "reason" in item:
                table.add_row(
                    str(item["line_number"]),
                    item["raw_line"],
                    item["reason"]
                )
            else:
                table.add_row(
                    str(item["line_number"]),
                    item["raw_line"],
                    "-"
                )

        console.print(table)


def show_banner(repo):
    console.print(
        Panel.fit(
            (
                "[bold green]Log Analyzer CLI[/bold green]\n"
                f"Total lines: {repo.total_lines}\n"
                f"Valid entries: {len(repo.entries)}\n"
                f"Malformed entries: {len(repo.malformed_lines)}\n"
                f"Unique IPs: {len(repo.by_ip)}\n"
                f"Unique endpoints: {len(repo.by_endpoint)}"
            )
        )
    )


def show_help():
    console.print("""
[bold cyan]Available Commands[/bold cyan]

report                Overall summary
slowest               Top slow endpoints
errors                Show 4xx / 5xx logs
anomalies             Show malformed logs
endpoint <path>       Inspect endpoint
ip <address>          Trace IP
status <code>         Query status code
method <method>       Query HTTP method
search <text>         Search raw logs

next                  Next page
prev                  Previous page

help                  Show commands
exit                  Exit
""")


def print_message(msg, color="green"):
    console.print(f"[{color}]{msg}[/{color}]")