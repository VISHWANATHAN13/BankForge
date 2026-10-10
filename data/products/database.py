import csv
import os
import sqlite3
from pathlib import Path
import csv
from datetime import datetime

from common.logging_config import get_logger, trace


logger = get_logger(__name__)

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = BASE_DIR / "data" / "products" / "products.db"
DEFAULT_APPLICATIONS_PATH = (
    BASE_DIR / "data" / "products" / "loan_applications.csv"
)

DB_PATH = Path(
    os.getenv("PRODUCTS_DB_PATH", DEFAULT_DB_PATH)
)

APPLICATIONS_PATH = Path(
    os.getenv("LOAN_APPLICATIONS_PATH", DEFAULT_APPLICATIONS_PATH)
)


def _connect():
    """Create a connection to the Products database."""

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
    """Create and seed the Products database."""

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    if force and DB_PATH.exists():
        DB_PATH.unlink()

    with _connect() as conn:

        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS loan_products (
                product_id TEXT PRIMARY KEY,
                product_name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                min_amount REAL NOT NULL,
                max_amount REAL NOT NULL,
                interest_rate REAL NOT NULL,
                tenure_months INTEGER NOT NULL,
                min_risk_rating TEXT NOT NULL
            );
            """
        )

        existing_count = conn.execute(
            "SELECT COUNT(*) FROM loan_products"
        ).fetchone()[0]

        if existing_count == 0:

            products = [
                (
                    "PROD-LN-01",
                    "Personal Loan",
                    "personal",
                    "Unsecured personal loan for general financial needs.",
                    50000,
                    500000,
                    11.5,
                    60,
                    "LOW",
                ),
                (
                    "PROD-LN-02",
                    "Home Improvement Loan",
                    "home_improvement",
                    "Loan for approved home renovation and improvement expenses.",
                    100000,
                    1000000,
                    9.5,
                    84,
                    "LOW",
                ),
                (
                    "PROD-LN-03",
                    "Education Loan",
                    "education",
                    "Loan for eligible higher education expenses.",
                    100000,
                    1500000,
                    8.5,
                    120,
                    "MEDIUM",
                ),
                (
                    "PROD-LN-04",
                    "Vehicle Loan",
                    "vehicle",
                    "Loan for purchase of eligible new or used vehicles.",
                    100000,
                    2000000,
                    9.0,
                    84,
                    "MEDIUM",
                ),
            ]

            conn.executemany(
                """
                INSERT INTO loan_products (
                    product_id,
                    product_name,
                    category,
                    description,
                    min_amount,
                    max_amount,
                    interest_rate,
                    tenure_months,
                    min_risk_rating
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                products,
            )

        conn.commit()

    _ensure_application_file()

    logger.info(
        "Products database initialized",
        extra={
            "fields": {
                "database": str(DB_PATH),
                "applications_file": str(APPLICATIONS_PATH),
            }
        },
    )


def _ensure_application_file():
    """Create the loan application CSV if it does not exist."""
    
    print("APPLICATIONS_PATH:", APPLICATIONS_PATH)
    print("TYPE:", type(APPLICATIONS_PATH))

    APPLICATIONS_PATH.parent.mkdir(parents=True, exist_ok=True)

    if APPLICATIONS_PATH.exists():
        return APPLICATIONS_PATH

    headers = [
        "application_id",
        "customer_id",
        "product_id",
        "amount",
        "status",
        "submitted_at",
    ]

    sample_applications = [
        [
            "APP-00001",
            "CUS-00001",
            "PROD-LN-01",
            "200000",
            "APPROVED",
            "2026-09-20T10:30:00",
        ],
        [
            "APP-00002",
            "CUS-00002",
            "PROD-LN-03",
            "500000",
            "PENDING",
            "2026-09-25T14:15:00",
        ],
    ]

    with APPLICATIONS_PATH.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(headers)
        writer.writerows(sample_applications)
    return APPLICATIONS_PATH


@trace(logger)
def get_loan_product(product_id: str):
    """Return a single loan product."""

    with _connect() as conn:

        row = conn.execute(
            """
            SELECT
                product_id,
                product_name,
                category,
                description,
                min_amount,
                max_amount,
                interest_rate,
                tenure_months,
                min_risk_rating
            FROM loan_products
            WHERE product_id = ?
            """,
            (product_id,),
        ).fetchone()

    return dict(row) if row else None


@trace(logger)
def list_loan_products(category: str | None = None):
    """Return all loan products, optionally filtered by category."""

    with _connect() as conn:

        if category:
            rows = conn.execute(
                """
                SELECT
                    product_id,
                    product_name,
                    category,
                    description,
                    min_amount,
                    max_amount,
                    interest_rate,
                    tenure_months,
                    min_risk_rating
                FROM loan_products
                WHERE category = ?
                ORDER BY product_id
                """,
                (category,),
            ).fetchall()

        else:
            rows = conn.execute(
                """
                SELECT
                    product_id,
                    product_name,
                    category,
                    description,
                    min_amount,
                    max_amount,
                    interest_rate,
                    tenure_months,
                    min_risk_rating
                FROM loan_products
                ORDER BY product_id
                """
            ).fetchall()

    return [dict(row) for row in rows]


@trace(logger)
def get_loan_applications():
    """Read all loan applications from the CSV file."""

    _ensure_application_file()

    with APPLICATIONS_PATH.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)

        return list(reader)


@trace(logger)
def get_loan_application(application_id: str):
    """Return a single loan application."""

    applications = get_loan_applications()

    for application in applications:

        if application["application_id"] == application_id:
            return application

    return None


if __name__ == "__main__":

    init_db(force=True)

    print("=" * 60)
    print("BANKFORGE PRODUCTS DATABASE")
    print("=" * 60)

    products = list_loan_products()

    print(f"Products: {len(products)}")

    for product in products:
        print(
            f"{product['product_id']} | "
            f"{product['product_name']} | "
            f"{product['category']}"
        )

    applications = get_loan_applications()

    print(f"\nLoan applications: {len(applications)}")

    for application in applications:
        print(
            f"{application['application_id']} | "
            f"{application['customer_id']} | "
            f"{application['status']}"
        )

def create_loan_application(
    customer_id: str,
    product_id: str,
    requested_amount: float,
) -> dict:

    applications = get_loan_applications()

    next_number = len(applications) + 1
    application_id = f"APP-{next_number:05d}"

    application = {
        "application_id": application_id,
        "customer_id": customer_id,
        "product_id": product_id,
        "amount": str(requested_amount),
        "status": "PENDING",
        "submitted_at": datetime.now().isoformat(),
    }

    file_path = _ensure_application_file()

    with file_path.open(
        "a",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "application_id",
                "customer_id",
                "product_id",
                "amount",
                "status",
                "submitted_at",
            ],
        )

        writer.writerow(application)

    return application


def get_loan_application_status(application_id: str) -> dict | None:

    application = get_loan_application(application_id)

    if not application:
        return None

    return {
        "application_id": application["application_id"],
        "customer_id": application["customer_id"],
        "product_id": application["product_id"],
        "amount": float(application["amount"]),
        "status": application["status"],
        "submitted_at": application["submitted_at"],
    }