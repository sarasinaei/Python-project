from rich.console import Console
from rich.table import Table
from rich import box


def display_table(names):
    #Create table
    table = Table(title="names", box=box.ROUNDED, show_lines=True,
                  header_style="bold magenta", row_styles=[" ", "dim"])
    # Define table columns
    table.add_column("No.", style="cyan", no_wrap=True)
    table.add_column("Name", justify="right", style="green")

    for num, name in enumerate(names, start=1):
        table.add_row(str(num), name)

    return table


def main():
    names = []
    # Get 5 names from the user
    for i in range(5):
        name = input(f"Enter name {i + 1}: ")
        names.append(name)

    table = display_table(names)
    Console().print(table)

main()
