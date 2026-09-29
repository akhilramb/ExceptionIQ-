import sqlite3
from datetime import datetime
from typing import List, Optional
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "exceptions.db"
HINDSIGHT_DB_PATH = Path(__file__).parent.parent / "data" / "mock-hindsight.db"

def init_database():
    """Initialize SQLite database with exceptions table"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS exceptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor TEXT NOT NULL,
                invoice_number TEXT,
                po_number TEXT,
                invoice_amount REAL,
                po_amount REAL,
                difference REAL,
                exception_type TEXT,
                description TEXT,
                status TEXT DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print(f"[OK] Database initialized at {DB_PATH}")

def init_hindsight_db():
    """Initialize mock Hindsight database with demo memories"""
    HINDSIGHT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(HINDSIGHT_DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor TEXT NOT NULL,
                problem_type TEXT NOT NULL,
                amount_difference REAL,
                root_cause TEXT,
                solution TEXT,
                outcome TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert demo memories
        demo_memories = [
            ('NovaTech Solutions', 'Invoice Amount Mismatch', 6500, 'Freight charge', 'Verify freight agreement', 'successful'),
            ('NovaTech Solutions', 'Invoice Amount Mismatch', 9200, 'Freight charge', 'Procurement verification', 'successful'),
            ('Bharat Logistics', 'Missing GST', 18000, 'GST not included in invoice', 'Request GST invoice document', 'successful'),
            ('Vertex Systems', 'Duplicate Invoice', 75000, 'Duplicate invoice number', 'Contact vendor to correct', 'successful'),
            ('Vertex Systems', 'Incorrect PO', 42000, 'PO amount different', 'Verify original PO', 'successful'),
            ('Deccan Supplies', 'Unexpected Charges', 5500, 'Miscellaneous charges', 'Ask vendor for breakdown', 'successful'),
            ('NovaTech Solutions', 'Taxes Mismatch', 4800, 'Service tax not included', 'Request tax details', 'successful'),
            ('Bharat Logistics', 'Delivery Charges', 3200, 'Extra delivery charges', 'Check delivery terms', 'successful'),
            ('Vertex Systems', 'Discount Issue', 7800, 'Discount not applied', 'Verify discount policy', 'successful'),
            ('Deccan Supplies', 'Partial Invoice', 42000, 'Partial payment made', 'Check partial invoice status', 'successful'),
            ('NovaTech Solutions', 'Freight Varies', 5600, 'Freight amount changed', 'Compare with agreement', 'successful'),
            ('Bharat Logistics', 'Taxes Updated', 6200, 'New tax rate applicable', 'Update tax calculation', 'successful'),
            ('Vertex Systems', 'Payment Terms', 9400, 'Payment terms unclear', 'Get written confirmation', 'successful'),
            ('Deccan Supplies', 'Quantity Discrepancy', 3800, 'Higher quantity delivered', 'Verify delivery note', 'successful'),
            ('NovaTech Solutions', 'Invoice Date', 4500, 'Invoice date mismatch', 'Check document validity', 'successful'),
            ('Bharat Logistics', 'Platform Fee', 2800, 'Platform charges extra', 'Review contract terms', 'successful'),
            ('Vertex Systems', 'Unit Price Variation', 5900, 'Unit price changed', 'Check amendment', 'successful'),
            ('Deccan Supplies', 'Payment Method', 4100, 'Payment method changed', 'Confirm new method', 'successful'),
            ('NovaTech Solutions', 'Subtotal Mismatch', 3600, 'Subtotal calculation error', 'Verify calculation', 'successful'),
            ('Bharat Logistics', 'Credit Note', 4700, 'Credit note not applied', 'Request credit note', 'successful'),
            ('Vertex Systems', 'Delivery Delay', 8100, 'Delivery delayed', 'Check shipping schedule', 'successful'),
        ]

        conn.executemany("""
            INSERT INTO memories (vendor, problem_type, amount_difference, root_cause, solution, outcome)
            VALUES (?, ?, ?, ?, ?, ?)
        """, demo_memories)
        print(f"[OK] Mock Hindsight database initialized with {len(demo_memories)} memories")


def get_all_exceptions() -> List[dict]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM exceptions ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]


def get_exception_by_id(exception_id: int) -> Optional[dict]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM exceptions WHERE id = ?", (exception_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def create_exception(data: dict) -> dict:
    """Create a new exception record"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            INSERT INTO exceptions (vendor, invoice_number, po_number, invoice_amount,
                                   po_amount, difference, exception_type, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['vendor'],
            data.get('invoice_number', ''),
            data.get('po_number', ''),
            data['invoice_amount'],
            data['po_amount'],
            data.get('difference', 0),
            data['exception_type'],
            data.get('description', '')
        ))
        conn.commit()
        return {**data, 'id': cursor.lastrowid}


def update_exception(exception_id: int, updates: dict) -> dict:
    """Update exception status"""
    with sqlite3.connect(DB_PATH) as conn:
        fields = []
        values = []
        for key, value in updates.items():
            if key not in ['id']:
                fields.append(f"{key} = ?")
                values.append(value)
        values.append(exception_id)

        sql = f"UPDATE exceptions SET {', '.join(fields)} WHERE id = ?"
        conn.execute(sql, values)
        conn.commit()
        return get_exception_by_id(exception_id)


def get_memories_by_vendor(vendor: str) -> List[dict]:
    """Get memories for a specific vendor (simulates Hindsight recall)"""
    with sqlite3.connect(HINDSIGHT_DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT * FROM memories WHERE vendor = ?
            ORDER BY created_at DESC
        """, (vendor,))
        return [dict(row) for row in cursor.fetchall()]


def add_memory(dict) -> dict:
    """Add a new memory (simulates Hindsight RETAIN)"""
    with sqlite3.connect(HINDSIGHT_DB_PATH) as conn:
        cursor = conn.execute("""
            INSERT INTO memories (vendor, problem_type, amount_difference, root_cause, solution, outcome)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data['vendor'],
            data['problem_type'],
            data.get('amount_difference', 0),
            data.get('root_cause', ''),
            data.get('solution', ''),
            data['outcome']
        ))
        conn.commit()
        return {
            'id': cursor.lastrowid,
            **data
        }


# Initialize on import
init_database()
init_hindsight_db()