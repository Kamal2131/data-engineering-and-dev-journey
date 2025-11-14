"""
Bank Account System (OOP) - Full Project
========================================

Description
-----------
This single-file Python project demonstrates a complete OOP-based Bank Account
system. It includes:

- Account base class
- SavingsAccount (interest)
- CurrentAccount (overdraft)
- Transaction storage and persistence (JSON)
- AccountManager to create, load, save, and manage multiple accounts
- A simple command-line interface (CLI) for interactive use
- Basic input validation and error handling

Files created by the program
----------------------------
- accounts.json           -> stores account metadata and balances
- <account_name>_transactions.json -> stores a list of transactions per account

How to run
----------
1. Requires Python 3.8+
2. Run: python day6_oops_bank.py
3. Follow the menu to create accounts, deposit, withdraw, show balance, add interest, save, and load.

Optional: run `python day6_oops_bank.py --demo` to populate sample accounts.

Notes
-----
- Account names are used as file-safe keys for saving transactions. Avoid using
  special characters in account names for portability.
- This is intentionally a single-file project to be easy to copy into your repo.
"""

import json
import os
import sys
import datetime
from typing import List, Dict, Any

# -----------------------------
# Models
# -----------------------------
class Account:
    """Base Account class."""

    def __init__(self, name: str, balance: float = 0.0):
        self.name = name
        self.balance = float(balance)
        self.transactions: List[Dict[str, Any]] = []

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        self._record("DEPOSIT", amount)

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount <= self.balance:
            self.balance -= amount
            self._record("WITHDRAW", amount)
        else:
            raise ValueError("Insufficient funds")

    def get_balance(self) -> float:
        return self.balance

    def _record(self, kind: str, amount: float) -> None:
        self.transactions.append({
            "type": kind,
            "amount": amount,
            "balance": self.balance,
            "timestamp": datetime.datetime.now().isoformat(),
        })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "class": self.__class__.__name__,
            "name": self.name,
            "balance": self.balance,
            "transactions": self.transactions,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]):
        acct = cls(d["name"], d.get("balance", 0.0))
        acct.transactions = d.get("transactions", [])
        return acct


class SavingsAccount(Account):
    """Savings account with a simple interest method."""

    def __init__(self, name: str, balance: float = 0.0, interest_rate: float = 0.02):
        super().__init__(name, balance)
        self.interest_rate = interest_rate

    def add_interest(self) -> float:
        interest = self.balance * self.interest_rate
        self.balance += interest
        self._record("INTEREST", interest)
        return interest

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d["interest_rate"] = self.interest_rate
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]):
        acct = cls(d["name"], d.get("balance", 0.0), d.get("interest_rate", 0.02))
        acct.transactions = d.get("transactions", [])
        return acct


class CurrentAccount(Account):
    """Current account with an overdraft limit."""

    def __init__(self, name: str, balance: float = 0.0, overdraft_limit: float = 5000.0):
        super().__init__(name, balance)
        self.overdraft_limit = overdraft_limit

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount <= self.balance + self.overdraft_limit:
            self.balance -= amount
            self._record("WITHDRAW", amount)
        else:
            raise ValueError("Exceeded overdraft limit")

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d["overdraft_limit"] = self.overdraft_limit
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]):
        acct = cls(d["name"], d.get("balance", 0.0), d.get("overdraft_limit", 5000.0))
        acct.transactions = d.get("transactions", [])
        return acct


# -----------------------------
# Persistence
# -----------------------------
class TransactionStorage:
    """Utility to save transactions for an account into a JSON file."""

    @staticmethod
    def filename_for(account_name: str) -> str:
        safe = "".join([c for c in account_name if c.isalnum() or c in "-_ "]).rstrip()
        return f"{safe}_transactions.json"

    @staticmethod
    def save(account: Account) -> None:
        fname = TransactionStorage.filename_for(account.name)
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(account.transactions, f, indent=4)

    @staticmethod
    def load(account: Account) -> None:
        fname = TransactionStorage.filename_for(account.name)
        if os.path.exists(fname):
            with open(fname, "r", encoding="utf-8") as f:
                account.transactions = json.load(f)


# -----------------------------
# Account Manager
# -----------------------------
class AccountManager:
    """Manages multiple accounts and persistence to a single accounts.json file."""

    STORAGE_FILE = "accounts.json"

    def __init__(self):
        self.accounts: Dict[str, Account] = {}

    def create_account(self, acct_type: str, name: str, balance: float = 0.0, **kwargs) -> Account:
        if name in self.accounts:
            raise ValueError("Account with this name already exists")
        acct_type = acct_type.lower()
        if acct_type == "savings":
            acct = SavingsAccount(name, balance, kwargs.get("interest_rate", 0.02))
        elif acct_type == "current":
            acct = CurrentAccount(name, balance, kwargs.get("overdraft_limit", 5000.0))
        else:
            acct = Account(name, balance)
        self.accounts[name] = acct
        return acct

    def get(self, name: str) -> Account:
        if name not in self.accounts:
            raise KeyError("Account not found")
        return self.accounts[name]

    def delete(self, name: str) -> None:
        if name in self.accounts:
            del self.accounts[name]

    def save_all(self) -> None:
        data = {name: acct.to_dict() for name, acct in self.accounts.items()}
        with open(self.STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        # save each transactions file too
        for acct in self.accounts.values():
            TransactionStorage.save(acct)

    def load_all(self) -> None:
        if not os.path.exists(self.STORAGE_FILE):
            return
        with open(self.STORAGE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for name, d in data.items():
            clsname = d.get("class", "Account")
            if clsname == "SavingsAccount":
                acct = SavingsAccount.from_dict(d)
            elif clsname == "CurrentAccount":
                acct = CurrentAccount.from_dict(d)
            else:
                acct = Account.from_dict(d)
            # try to load transactions if present on disk
            TransactionStorage.load(acct)
            self.accounts[name] = acct


# -----------------------------
# CLI Helpers
# -----------------------------

def _input_float(prompt: str) -> float:
    while True:
        try:
            val = input(prompt).strip()
            return float(val)
        except ValueError:
            print("Please enter a valid number.")


def _input_nonempty(prompt: str) -> str:
    while True:
        val = input(prompt).strip()
        if val:
            return val
        print("Value cannot be empty.")


def display_account(acct: Account) -> None:
    print("-----------------------------------")
    print(f"Name:   {acct.name}")
    print(f"Type:   {acct.__class__.__name__}")
    print(f"Balance:{acct.balance:.2f}")
    if isinstance(acct, SavingsAccount):
        print(f"Interest rate: {acct.interest_rate}")
    if isinstance(acct, CurrentAccount):
        print(f"Overdraft limit: {acct.overdraft_limit}")
    print("Transactions: ")
    for t in acct.transactions[-10:]:
        ts = t.get("timestamp", "N/A")
        typ = t.get("type", "N/A")
        amt = t.get("amount", "N/A")
        bal = t.get("balance", "N/A")
        print(f"  - {ts} | {typ} | {amt} | Bal: {bal}")
    print("-----------------------------------")


# -----------------------------
# Demo data
# -----------------------------

def populate_demo(manager: AccountManager) -> None:
    try:
        a = manager.create_account("savings", "Kamal", 1000)
        a.deposit(500)
        a.withdraw(200)
        a.add_interest()
        b = manager.create_account("current", "Ranit", 300)
        b.deposit(1200)
        b.withdraw(100)
        manager.save_all()
        print("Demo accounts created: Kamal (Savings), Ranit (Current)")
    except Exception as e:
        print("Demo error:", e)


# -----------------------------
# Main CLI Loop
# -----------------------------

def main(argv=None):
    argv = argv or sys.argv[1:]
    manager = AccountManager()
    manager.load_all()

    if "--demo" in argv:
        populate_demo(manager)

    while True:
        print("\n=== Bank Account System ===")
        print("1. Create account")
        print("2. List accounts")
        print("3. Show account")
        print("4. Deposit")
        print("5. Withdraw")
        print("6. Add interest (Savings only)")
        print("7. Save all")
        print("8. Delete account")
        print("9. Exit")

        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                name = _input_nonempty("Account name: ")
                typ = _input_nonempty("Type (savings/current/other): ")
                bal = _input_float("Initial balance: ")
                extra = {}
                if typ.lower() == "savings":
                    r = input("Interest rate (default 0.02): ").strip()
                    extra["interest_rate"] = float(r) if r else 0.02
                if typ.lower() == "current":
                    o = input("Overdraft limit (default 5000): ").strip()
                    extra["overdraft_limit"] = float(o) if o else 5000.0
                acct = manager.create_account(typ, name, bal, **extra)
                TransactionStorage.save(acct)
                print("Account created.")

            elif choice == "2":
                if not manager.accounts:
                    print("No accounts found.")
                else:
                    for name in manager.accounts:
                        print("-", name)

            elif choice == "3":
                name = _input_nonempty("Account name: ")
                acct = manager.get(name)
                display_account(acct)

            elif choice == "4":
                name = _input_nonempty("Account name: ")
                acct = manager.get(name)
                amt = _input_float("Amount to deposit: ")
                acct.deposit(amt)
                TransactionStorage.save(acct)
                print("Deposited.")

            elif choice == "5":
                name = _input_nonempty("Account name: ")
                acct = manager.get(name)
                amt = _input_float("Amount to withdraw: ")
                acct.withdraw(amt)
                TransactionStorage.save(acct)
                print("Withdrawn.")

            elif choice == "6":
                name = _input_nonempty("Account name: ")
                acct = manager.get(name)
                if isinstance(acct, SavingsAccount):
                    interest = acct.add_interest()
                    TransactionStorage.save(acct)
                    print(f"Interest added: {interest:.2f}")
                else:
                    print("This is not a Savings account.")

            elif choice == "7":
                manager.save_all()
                print("All accounts saved to disk.")

            elif choice == "8":
                name = _input_nonempty("Account name to delete: ")
                manager.delete(name)
                manager.save_all()
                # optionally remove transactions file
                fname = TransactionStorage.filename_for(name)
                try:
                    if os.path.exists(fname):
                        os.remove(fname)
                except Exception:
                    pass
                print("Deleted (if existed) and saved.")

            elif choice == "9":
                print("Goodbye!")
                break

            else:
                print("Invalid option. Try again.")

        except KeyError:
            print("Account not found. Try creating one first.")
        except ValueError as e:
            print("Error:", e)
        except Exception as e:
            print("Unexpected error:", e)


if __name__ == "__main__":
    main()
