import os
import psutil
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.prompt import Prompt
from rich.columns import Columns

console = Console()

def list_directory(path):
    table = Table(title="File Manager", box=box.ROUNDED)
    table.add_column("Name", justify="left", style="cyan", no_wrap=True)
    table.add_column("Type", justify="center", style="magenta")
    table.add_column("Size", justify="right", style="green")

    try:
        with os.scandir(path) as entries:
            for entry in entries:
                entry_type = "Dir" if entry.is_dir() else "File"
                entry_size = os.path.getsize(entry) if entry.is_file() else "-"
                table.add_row(entry.name, entry_type, str(entry_size))
    except PermissionError:
        console.print("[red]Permission Denied[/red]")
        return

    return table

def list_processes():
    table = Table(title="Processes", box=box.ROUNDED)
    table.add_column("PID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Name", justify="left", style="magenta")
    table.add_column("Status", justify="left", style="green")
    table.add_column("Memory", justify="right", style="yellow")

    for proc in psutil.process_iter(['pid', 'name', 'status', 'memory_info']):
        try:
            table.add_row(str(proc.info['pid']), proc.info['name'], proc.info['status'], str(proc.info['memory_info'].rss))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return table

def list_disks():
    table = Table(title="Disk Usage", box=box.ROUNDED)
    table.add_column("Device", justify="left", style="cyan", no_wrap=True)
    table.add_column("Mountpoint", justify="left", style="magenta")
    table.add_column("Total", justify="right", style="green")
    table.add_column("Used", justify="right", style="yellow")
    table.add_column("Free", justify="right", style="red")
    table.add_column("Percentage", justify="right", style="blue")

    for partition in psutil.disk_partitions():
        usage = psutil.disk_usage(partition.mountpoint)
        table.add_row(partition.device, partition.mountpoint, str(usage.total), str(usage.used), str(usage.free), f"{usage.percent}%")

    return table

def main():
    current_path = os.getcwd()
    
    while True:
        console.clear()
        file_table = list_directory(current_path)
        process_table = list_processes()
        disk_table = list_disks()
        
        columns = Columns([Panel(file_table, border_style="blue", title="Files"), 
                           Panel(process_table, border_style="green", title="Processes"), 
                           Panel(disk_table, border_style="magenta", title="Disks")])

        console.print(columns)
        
        command = Prompt.ask("Enter a command (cd [dir], up, quit)")
        if command.startswith("cd "):
            new_path = command[3:]
            if os.path.isdir(new_path):
                current_path = os.path.abspath(new_path)
            else:
                console.print("[red]Directory not found[/red]")
        elif command == "up":
            current_path = os.path.dirname(current_path)
        elif command == "quit":
            break
        else:
            console.print("[red]Unknown command[/red]")

if __name__ == "__main__":
    main()
