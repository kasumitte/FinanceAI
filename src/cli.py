import argparse
import logging
import os
from rich.console import Console
from rich.table import Table
from pathlib import Path
from datetime import datetime
from src.importer import import_transactions
from src.categorizer import get_AIResponse
from src.analytics import get_monthly_stats, get_TopTA
from src.database import get_RawTransactions
from src.charts import generate_category_chart, generate_TopTransactions_chart

logging.basicConfig(level=logging.INFO,
                    format="[%(levelname)s][%(asctime)s]: %(message)s")
logger = logging.getLogger(__name__)


class App:
    def __init__(self, pool, client, outpath):
        self.pool = pool
        self.client = client
        self.outpath = outpath
        self.console = Console()
        
    def show_all_transactions(self, stat: list):
        if not stat:
            self.console.print("History is empty", style="bold red")
            return
        
        table = Table(title="All Transactions", header_style="bold magenta")
        table.add_column("Description", style="cyan", width=15)
        table.add_column("Amount", style="cyan", width=15)
        table.add_column("Category", style="cyan", width=15)
    
        for row in stat:
            table.add_row(
                row['description'],
                str(round(row['amount'], 2)),
                str(row['category_id']) if row['category_id'] else "uncategorized"
            )
        self.console.print(table)
        
    def show_top_transactions(self, stat: list):
        if not stat:
            self.console.print("History is empty", style="bold red")
            return
        
        table = Table(title="Top Transactions", header_style="bold magenta")
        table.add_column("ID", style="cyan", width=10)
        table.add_column("Date", style="cyan", width=15)
        table.add_column("Description", style="cyan", width=15)
        table.add_column("Amount", style="cyan", width=15)
        table.add_column("Category", style="cyan", width=15)
        
        for row in stat:
            table.add_row(
                str(row['id']),
                row['date'],
                row['description'],
                str(row['amount']),
                row['name']
            )
        self.console.print(table)
        
    
    def setup_args(self):
        parser = argparse.ArgumentParser(description="AI Finance Tracker")
        subparsers = parser.add_subparsers(dest="command")

        import_parser = subparsers.add_parser("import", help="Import CSV file")
        import_parser.add_argument("--file", required=True, help="Path to CSV file")
        
        stats_parser = subparsers.add_parser("stats", help="Show montly stats")
        stats_parser.add_argument("--month", required=True, help="Month in YYYY-MM format")
        
        graph_parser = subparsers.add_parser("graph", help="Visualize data")
        group = graph_parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--top", type=int, default=None, help="Build Top N graph (specify N)")
        group.add_argument("--all", action="store_true", help="Build graph with all statistics")
        
        subparsers.add_parser("categorize", help="Categorize transactions with AI")
        
        top_parser = subparsers.add_parser("top", help="Show top transactions")     
        top_parser.add_argument("--n", type=int, default=10, help="Number of transactions")
        
        subparsers.add_parser("list", help="List of all transactions")      
    
        return parser
    
    async def run(self):
        """ Main workflow """
        parser = self.setup_args()
        args = parser.parse_args()
        
        match args.command:
            case "import":
                file_path = args.file
                if not os.path.exists(file_path) or os.path.isdir(file_path):
                    logger.error(f"Path does not exist") 
                    return
                
                result = await import_transactions(self.pool, Path(file_path)) # type: ignore
                if result:
                    self.console.print("Import was successfully done", style="bold green")
                else:
                    self.console.print("Importing failed", style="bold red")
                
            case "stats":
                result = await get_monthly_stats(self.pool, args.month)
                if result is None:
                    self.console.print("History is empty or nothing was imported", style="bold red")
                    return
                
                month_dt = datetime.strptime(args.month, "%Y-%m")
                formatted = month_dt.strftime("%B %Y")
                self.console.print(f"Total for {formatted}: {float(result):.2f}", style="cyan")
                
            case "graph":
                if args.top is not None:
                    if await generate_TopTransactions_chart(self.pool, self.outpath, args.top):                        
                        self.console.print(f"Top graph was built in {str(self.outpath)} folder", style="bold cyan")
                    else:
                        self.console.print("No data was given", style="bold red")
                    
                elif args.all:
                    if await generate_category_chart(self.pool, self.outpath):                        
                        self.console.print(f"Graph with all statistic was built in {str(self.outpath)} folder", style="bold cyan")
                    else:
                        self.console.print("No data was given", style="bold red")
                    
            case "categorize":
                try:
                    result = await get_AIResponse(self.client, self.pool)
                    self.console.print("Done!", style="bold green")
                except Exception:
                    self.console.print("Categorization failed", style="bold red")
            
            case "top":
                try:
                    stats = await get_TopTA(self.pool, args.n)
                    self.show_top_transactions(stats)
                except Exception:
                    self.console.print(f"No category field to generate top, firstly do 'categorize'", style="bold red")
            
            case "list":
                stats = await get_RawTransactions(self.pool)
                self.show_all_transactions(stats)
            
            case _:
                parser.print_help()
                
