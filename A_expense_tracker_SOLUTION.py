"""
Midterm Exam - Version A: Expense Tracker      (SOLUTION - instructor copy)
Menu: 1 Add | 2 List | 3 Statistics | 4 Filter | 5 Chart | 6 Convert | 7 Password | 8 Exit
"""
import os
import getpass
import requests
import matplotlib.pyplot as plt

# ======================= Colors =======================
RED, GREEN, YELLOW, BLUE, CYAN, RESET = (
    "\033[91m", "\033[92m", "\033[93m", "\033[94m", "\033[96m", "\033[0m")
os.system("")  # enables ANSI colors in Windows cmd

# ======================= Data =======================
credentials = {"username": "admin", "password": "Py@12345"}

expenses = [
    {"amount": 12.5, "category": "Food", "note": "Lunch"},
    {"amount": 40.0, "category": "Transport", "note": "Taxi"},
    {"amount": 25.0, "category": "Food", "note": "Dinner"},
    {"amount": 80.0, "category": "Shopping", "note": "Shoes"},
    {"amount": 15.0, "category": "Entertainment", "note": "Cinema"},
]

RATES_URL = "https://open.er-api.com/v6/latest/USD"  # no API key needed

# approximate rates used when the internet / API is not available (1 USD = ...)
FALLBACK_RATES = {"EUR": 0.92, "GBP": 0.79, "TRY": 35.0, "JPY": 150.0}


# ======================= Skeleton =======================
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    print(CYAN + r"""
  +-----------------------------------+
  |   $$  EXPENSE  TRACKER  v1.0  $$  |
  +-----------------------------------+
""" + RESET)


def login(max_attempts=3):
    for attempt in range(1, max_attempts + 1):
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")
        if username == credentials["username"] and password == credentials["password"]:
            print(GREEN + "Login successful!" + RESET)
            return True
        print(RED + f"Wrong username or password ({attempt}/{max_attempts})" + RESET)
    return False


def print_menu():
    print(YELLOW + "=========== MENU ===========" + RESET)
    items = ["Add expense", "Show expenses", "Statistics", "Filter by category",
             "Chart", "Convert total to another currency", "Change password", "Exit"]
    for number, title in enumerate(items, 1):
        print(f"  {BLUE}{number}{RESET}. {title}")


# ======================= Helpers =======================
def read_positive_float(prompt):
    while True:
        text = input(prompt).strip()
        try:
            value = float(text)
            if value > 0:
                return value
            print(RED + "Value must be greater than zero." + RESET)
        except ValueError:
            print(RED + "Please enter a valid number." + RESET)


def check_password_strength(password):
    """Return a list of problems (empty list = strong password)."""
    problems = []
    if len(password) < 8:
        problems.append("at least 8 characters")
    if not any(c.isupper() for c in password):
        problems.append("at least one uppercase letter")
    if not any(c.islower() for c in password):
        problems.append("at least one lowercase letter")
    if not any(c.isdigit() for c in password):
        problems.append("at least one digit")
    if password.isalnum():
        problems.append("at least one special character")
    return problems


# ======================= Options =======================
def add_expense():
    amount = read_positive_float("Amount ($): ")
    category = input("Category: ").strip().title() or "Other"
    note = input("Note: ").strip()
    expenses.append({"amount": amount, "category": category, "note": note})
    print(GREEN + "Expense added." + RESET)


def show_expenses(items=None):
    items = expenses if items is None else items
    if not items:
        print(RED + "No expenses found." + RESET)
        return
    print(f"{'#':<4}{'Amount':>10}  {'Category':<15}Note")
    print("-" * 45)
    for index, e in enumerate(items, 1):
        print(f"{index:<4}{e['amount']:>10.2f}  {e['category']:<15}{e['note']}")


def show_stats():
    if not expenses:
        print(RED + "No expenses yet." + RESET)
        return
    total = sum(e["amount"] for e in expenses)
    biggest = max(expenses, key=lambda e: e["amount"])
    print(f"Count   : {len(expenses)}")
    print(f"Total   : {total:.2f} $")
    print(f"Average : {total / len(expenses):.2f} $")
    print(f"Largest : {biggest['amount']:.2f} $  ({biggest['category']} - {biggest['note']})")


def filter_by_category():
    category = input("Category to search: ").strip().lower()
    result = [e for e in expenses if e["category"].lower() == category]
    show_expenses(result)
    if result:
        print(f"Total of this category: {sum(e['amount'] for e in result):.2f} $")


def show_chart():
    if not expenses:
        print(RED + "Nothing to draw." + RESET)
        return
    totals = {}
    for e in expenses:
        totals[e["category"]] = totals.get(e["category"], 0) + e["amount"]
    plt.figure(figsize=(7, 5))
    plt.bar(list(totals.keys()), list(totals.values()), color="steelblue")
    plt.title("Expenses by category")
    plt.xlabel("Category")
    plt.ylabel("Amount ($)")
    plt.show()


def get_rate(target):
    """Return (rate, is_live). Falls back to FALLBACK_RATES on any error."""
    try:
        response = requests.get(RATES_URL, timeout=10)
        response.raise_for_status()          # HTTP 4xx/5xx (e.g. 429 rate limit) -> HTTPError
        data = response.json()
        if data.get("result") != "success":  # API-level error
            raise ValueError(data.get("error-type", "unknown error"))
        return data["rates"][target], True
    except (requests.RequestException, KeyError, ValueError):
        return FALLBACK_RATES.get(target), False


def convert_total():
    if not expenses:
        print(RED + "No expenses yet." + RESET)
        return
    target = input("Target currency (EUR, GBP, TRY, JPY ...): ").strip().upper()
    rate, live = get_rate(target)
    if rate is None:
        print(RED + "Currency is not supported." + RESET)
        return
    total = sum(e["amount"] for e in expenses)
    print(f"Total: {total:.2f} USD = {total * rate:.2f} {target}")
    if not live:
        print(YELLOW + "(offline - approximate rate used)" + RESET)


def change_password():
    if getpass.getpass("Current password: ") != credentials["password"]:
        print(RED + "Current password is wrong." + RESET)
        return
    new_password = getpass.getpass("New password: ")
    problems = check_password_strength(new_password)
    if problems:
        print(RED + "Weak password. Required:" + RESET)
        for p in problems:
            print("  -", p)
        return
    if getpass.getpass("Repeat new password: ") != new_password:
        print(RED + "Passwords do not match." + RESET)
        return
    credentials["password"] = new_password
    print(GREEN + "Password changed." + RESET)


# ======================= Main =======================
def main():
    clear_screen()
    print_banner()
    if not login():
        print(RED + "Too many failed attempts. Goodbye." + RESET)
        return
    while True:
        clear_screen()
        print_banner()
        print_menu()
        choice = input("\nYour choice: ").strip()
        if choice == "8":
            print(GREEN + "Goodbye!" + RESET)
            break
        elif choice == "1":
            add_expense()
        elif choice == "2":
            show_expenses()
        elif choice == "3":
            show_stats()
        elif choice == "4":
            filter_by_category()
        elif choice == "5":
            show_chart()
        elif choice == "6":
            convert_total()
        elif choice == "7":
            change_password()
        else:
            print(RED + "Invalid choice. Enter a number between 1 and 8." + RESET)
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
