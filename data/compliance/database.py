import os
import sqlite3
from pathlib import Path

from common.logging_config import get_logger, trace


logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parents[2]

DEFAULT_DB_PATH = (
    BASE_DIR / "data" / "compliance" / "compliance.db"
)

DB_PATH = Path(
    os.getenv("COMPLIANCE_DB_PATH", DEFAULT_DB_PATH)
)


def _connect():
    """Create a connection to the Compliance database."""

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        DB_PATH,
        timeout=10,
    )

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA foreign_keys=ON")

    return connection


@trace(logger)
def init_db(force: bool = False):
    """Create and seed the Compliance database."""

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    if force and DB_PATH.exists():
        DB_PATH.unlink()

    with _connect() as conn:

        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL,
                kyc_status TEXT NOT NULL,
                customer_tier TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS fraud_flags (
                flag_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                flag_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (customer_id)
                    REFERENCES customers(customer_id)
            );

            CREATE TABLE IF NOT EXISTS communications (
                communication_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                channel TEXT NOT NULL,
                message TEXT NOT NULL,
                sent_at TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (customer_id)
                    REFERENCES customers(customer_id)
            );

            CREATE TABLE IF NOT EXISTS audit_log (
                audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action_type TEXT NOT NULL,
                performed_by TEXT NOT NULL,
                customer_id TEXT,
                outcome TEXT NOT NULL
            );
            """
        )

        customer_count = conn.execute(
            "SELECT COUNT(*) FROM customers"
        ).fetchone()[0]

        if customer_count == 0:

            customers = [
                (
                    "CUS-00001",
                    "Arjun Mehta",
                    "VERIFIED",
                    "PREMIUM",
                ),
                (
                    "CUS-00002",
                    "Priya Sharma",
                    "VERIFIED",
                    "STANDARD",
                ),
                (
                    "CUS-00003",
                    "Rahul Kumar",
                    "PENDING",
                    "STANDARD",
                ),
                (
                    "CUS-00004",
                    "Sneha Iyer",
                    "VERIFIED",
                    "PREMIUM",
                ),
                (
                    "CUS-00005",
                    "Vikram Singh",
                    "REJECTED",
                    "STANDARD",
                ),
            ]

            conn.executemany(
                """
                INSERT INTO customers (
                    customer_id,
                    customer_name,
                    kyc_status,
                    customer_tier
                )
                VALUES (?, ?, ?, ?)
                """,
                customers,
            )

        fraud_count = conn.execute(
            "SELECT COUNT(*) FROM fraud_flags"
        ).fetchone()[0]

        if fraud_count == 0:

            fraud_flags = [
                (
                    "FLAG-00001",
                    "CUS-00003",
                    "UNUSUAL_TRANSACTION",
                    "MEDIUM",
                    "Unusual transaction pattern detected.",
                    "OPEN",
                    "2026-09-20T09:30:00",
                ),
                (
                    "FLAG-00002",
                    "CUS-00005",
                    "IDENTITY_CONCERN",
                    "HIGH",
                    "Identity verification requires review.",
                    "OPEN",
                    "2026-09-21T11:00:00",
                ),
            ]

            conn.executemany(
                """
                INSERT INTO fraud_flags (
                    flag_id,
                    customer_id,
                    flag_type,
                    severity,
                    description,
                    status,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                fraud_flags,
            )

        conn.commit()

    logger.info(
        "Compliance database initialized",
        extra={
            "fields": {
                "database": str(DB_PATH),
            }
        },
    )


@trace(logger)
def get_customer(customer_id: str):
    """Return a customer compliance profile."""

    with _connect() as conn:

        row = conn.execute(
            """
            SELECT
                customer_id,
                customer_name,
                kyc_status,
                customer_tier
            FROM customers
            WHERE customer_id = ?
            """,
            (customer_id,),
        ).fetchone()

    return dict(row) if row else None


@trace(logger)
def get_kyc_status(customer_id: str):
    """Return the KYC status for a customer."""

    with _connect() as conn:

        row = conn.execute(
            """
            SELECT
                customer_id,
                kyc_status
            FROM customers
            WHERE customer_id = ?
            """,
            (customer_id,),
        ).fetchone()

    return dict(row) if row else None


@trace(logger)
def get_fraud_flags(customer_id: str):
    """Return fraud flags for a customer."""

    with _connect() as conn:

        rows = conn.execute(
            """
            SELECT
                flag_id,
                customer_id,
                flag_type,
                severity,
                description,
                status,
                created_at
            FROM fraud_flags
            WHERE customer_id = ?
            ORDER BY created_at DESC
            """,
            (customer_id,),
        ).fetchall()

    return [dict(row) for row in rows]


@trace(logger)
def add_communication(
    customer_id: str,
    channel: str,
    message: str,
    sent_at: str,
    status: str,
):
    """Store a customer communication record."""

    with _connect() as conn:

        cursor = conn.execute(
            """
            INSERT INTO communications (
                customer_id,
                channel,
                message,
                sent_at,
                status
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                customer_id,
                channel,
                message,
                sent_at,
                status,
            ),
        )

        conn.commit()

        return cursor.lastrowid


@trace(logger)
def write_audit_log(
    timestamp: str,
    action_type: str,
    performed_by: str,
    customer_id: str | None,
    outcome: str,
):
    """Write an audit entry for a write operation."""

    with _connect() as conn:

        cursor = conn.execute(
            """
            INSERT INTO audit_log (
                timestamp,
                action_type,
                performed_by,
                customer_id,
                outcome
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                timestamp,
                action_type,
                performed_by,
                customer_id,
                outcome,
            ),
        )

        conn.commit()

        return cursor.lastrowid


if __name__ == "__main__":

    init_db(force=True)

    print("=" * 60)
    print("BANKFORGE COMPLIANCE DATABASE")
    print("=" * 60)

    with _connect() as conn:

        customer_count = conn.execute(
            "SELECT COUNT(*) FROM customers"
        ).fetchone()[0]

        fraud_count = conn.execute(
            "SELECT COUNT(*) FROM fraud_flags"
        ).fetchone()[0]

        communication_count = conn.execute(
            "SELECT COUNT(*) FROM communications"
        ).fetchone()[0]

        audit_count = conn.execute(
            "SELECT COUNT(*) FROM audit_log"
        ).fetchone()[0]

    print(f"Customers: {customer_count}")
    print(f"Fraud flags: {fraud_count}")
    print(f"Communications: {communication_count}")
    print(f"Audit logs: {audit_count}")

def is_kyc_verified(customer_id: str) -> bool:
    customer = get_customer(customer_id)

    if not customer:
        return False

    return customer["kyc_status"].strip().upper() == "VERIFIED"