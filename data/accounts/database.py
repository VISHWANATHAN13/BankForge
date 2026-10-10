"""
BankForge - Accounts database.

Stores the Accounts domain data:
- Customers
- Accounts
- Transactions

This database is owned by the Accounts MCP server.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

# from .logging_config import get_logger, trace
from common.logging_config import get_logger, trace


logger = get_logger(__name__)

DB_PATH = Path(
    os.environ.get(
        "ACCOUNTS_DB_PATH",
        str(Path(__file__).parent / "accounts.db"),
    )
)


SCHEMA = """
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    kyc_status TEXT NOT NULL,
    risk_rating TEXT NOT NULL,
    segment TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS accounts (
    account_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    account_type TEXT NOT NULL,
    balance REAL NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    amount REAL NOT NULL,
    direction TEXT NOT NULL,
    description TEXT NOT NULL,
    txn_date TEXT NOT NULL,
    FOREIGN KEY (account_id)
        REFERENCES accounts(account_id)
);
"""


CUSTOMERS = [
    (
        "CUS-00001",
        "Ananya Rao",
        "ananya.rao@example.com",
        "9800000001",
        "verified",
        "low",
        "retail",
    ),
    (
        "CUS-00002",
        "Vikram Shah",
        "vikram.shah@example.com",
        "9800000002",
        "verified",
        "low",
        "business",
    ),
    (
        "CUS-00003",
        "Priya Nair",
        "priya.nair@example.com",
        "9800000003",
        "pending",
        "medium",
        "retail",
    ),
    (
        "CUS-00004",
        "Rohan Mehta",
        "rohan.mehta@example.com",
        "9800000004",
        "verified",
        "high",
        "retail",
    ),
    (
        "CUS-00005",
        "Sneha Iyer",
        "sneha.iyer@example.com",
        "9800000005",
        "verified",
        "low",
        "business",
    ),
    (
        "CUS-00006",
        "Arjun Kapoor",
        "arjun.kapoor@example.com",
        "9800000006",
        "rejected",
        "high",
        "retail",
    ),
]

ACCOUNTS = [
    ("ACC-00001", "CUS-00001", "savings", 85000.0, "active"),
    ("ACC-00002", "CUS-00002", "business", 1250000.0, "active"),
    ("ACC-00003", "CUS-00003", "savings", 12000.0, "active"),
    ("ACC-00004", "CUS-00004", "current", 500.0, "dormant"),
    ("ACC-00005", "CUS-00005", "business", 340000.0, "active"),
    ("ACC-00006", "CUS-00006", "savings", 0.0, "frozen"),
]

TRANSACTIONS = [
    (
        "TXN0001",
        "ACC-00001",
        15000.0,
        "credit",
        "Salary credit",
        "2025-11-01",
    ),
    (
        "TXN0002",
        "ACC-00001",
        2000.0,
        "debit",
        "ATM withdrawal",
        "2025-11-03",
    ),
    (
        "TXN0003",
        "ACC-00002",
        1050000.0,
        "credit",
        "Client payment received",
        "2025-11-05",
    ),
    (
        "TXN0004",
        "ACC-00002",
        300000.0,
        "debit",
        "Supplier payment",
        "2025-11-06",
    ),
    (
        "TXN0005",
        "ACC-00003",
        500.0,
        "debit",
        "UPI payment",
        "2025-11-07",
    ),
    (
        "TXN0006",
        "ACC-00005",
        75000.0,
        "credit",
        "Invoice settlement",
        "2025-11-08",
    ),
]


@trace(logger)
def _connect() -> sqlite3.Connection:
    """
    Create a connection to the Accounts database.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH, timeout=10)

    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    return conn


@trace(logger)
def init_db(force: bool = False) -> None:
    """
    Create and seed the Accounts database.
    """

    if force and DB_PATH.exists():
        DB_PATH.unlink()

    conn = _connect()

    conn.executescript(SCHEMA)

    conn.executemany(
        """
        INSERT OR IGNORE INTO customers
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        CUSTOMERS,
    )

    conn.executemany(
        """
        INSERT OR IGNORE INTO accounts
        VALUES (?, ?, ?, ?, ?)
        """,
        ACCOUNTS,
    )

    conn.executemany(
        """
        INSERT OR IGNORE INTO transactions
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        TRANSACTIONS,
    )

    conn.commit()
    conn.close()

    logger.info("Accounts database initialized: %s", DB_PATH)


@trace(logger)
def get_account(account_id: str) -> dict | None:
    """
    Retrieve one account by account ID.
    """

    conn = _connect()
    conn.row_factory = sqlite3.Row

    row = conn.execute(
        """
        SELECT *
        FROM accounts
        WHERE account_id = ?
        """,
        (account_id,),
    ).fetchone()

    conn.close()

    return dict(row) if row else None


@trace(logger)
def get_accounts_for_customer(customer_id: str) -> list[dict]:
    """
    Retrieve all accounts belonging to a customer.
    """

    conn = _connect()
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT *
        FROM accounts
        WHERE customer_id = ?
        """,
        (customer_id,),
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


@trace(logger)
def get_transactions(
    account_id: str,
    limit: int = 10,
) -> list[dict]:
    """
    Retrieve recent transactions for an account.
    """

    conn = _connect()
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT *
        FROM transactions
        WHERE account_id = ?
        ORDER BY txn_date DESC
        LIMIT ?
        """,
        (account_id, limit),
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


@trace(logger)
def get_customer(customer_id: str) -> dict | None:
    """
    Retrieve customer information by customer ID.
    """

    conn = _connect()
    conn.row_factory = sqlite3.Row

    row = conn.execute(
        """
        SELECT *
        FROM customers
        WHERE customer_id = ?
        """,
        (customer_id,),
    ).fetchone()

    conn.close()

    return dict(row) if row else None


if __name__ == "__main__":
    init_db(force=True)

    print(f"Seeded Accounts database: {DB_PATH}")
    print(f"Customers: {len(CUSTOMERS)}")
    print(f"Accounts: {len(ACCOUNTS)}")
    print(f"Transactions: {len(TRANSACTIONS)}")