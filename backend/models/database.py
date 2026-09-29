import sqlite3
from typing import List, Optional
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "exceptions.db"
HINDSIGHT_DB_PATH = Path(__file__).parent.parent / "data" / "mock-hindsight.db"


def _connect(path: Path):
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize the operational exception store."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS exceptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor TEXT NOT NULL,
                invoice_number TEXT,
                po_number TEXT,
                invoice_amount REAL NOT NULL,
                po_amount REAL NOT NULL,
                difference REAL NOT NULL DEFAULT 0,
                exception_type TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'open',
                resolution TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        columns = {row[1] for row in conn.execute("PRAGMA table_info(exceptions)")}
        if "resolution" not in columns:
            conn.execute("ALTER TABLE exceptions ADD COLUMN resolution TEXT")
        if "updated_at" not in columns:
            conn.execute("ALTER TABLE exceptions ADD COLUMN updated_at TIMESTAMP")


def init_hindsight_db():
    """Initialize a local memory store used as a Hindsight-compatible fallback."""
    HINDSIGHT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _connect(HINDSIGHT_DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor TEXT NOT NULL,
                problem_type TEXT NOT NULL,
                amount_difference REAL DEFAULT 0,
                root_cause TEXT,
                solution TEXT,
                outcome TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        count = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        if count == 0:
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
                ('Deccan Supplies', 'Quantity Discrepancy', 3800, 'Higher quantity delivered', 'Verify delivery note', 'successful'),
            ]
            conn.executemany("""
                INSERT INTO memories (vendor, problem_type, amount_difference, root_cause, solution, outcome)
                VALUES (?, ?, ?, ?, ?, ?)
            """, demo_memories)


def get_all_exceptions() -> List[dict]:
    with _connect(DB_PATH) as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM exceptions ORDER BY created_at DESC, id DESC").fetchall()]


def get_exception_by_id(exception_id: int) -> Optional[dict]:
    with _connect(DB_PATH) as conn:
        row = conn.execute("SELECT * FROM exceptions WHERE id = ?", (exception_id,)).fetchone()
        return dict(row) if row else None


def create_exception(data: dict) -> dict:
    with _connect(DB_PATH) as conn:
        cursor = conn.execute("""
            INSERT INTO exceptions (vendor, invoice_number, po_number, invoice_amount,
                po_amount, difference, exception_type, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['vendor'].strip(), data.get('invoice_number', '').strip(), data.get('po_number', '').strip(),
            data['invoice_amount'], data['po_amount'], data.get('difference', 0),
            data['exception_type'].strip(), data.get('description', '').strip()
        ))
        conn.commit()
        return get_exception_by_id(cursor.lastrowid)


def update_exception(exception_id: int, updates: dict) -> Optional[dict]:
    allowed = {'vendor', 'invoice_number', 'po_number', 'invoice_amount', 'po_amount', 'difference',
               'exception_type', 'description', 'status', 'resolution'}
    safe_updates = {k: v for k, v in updates.items() if k in allowed}
    if not safe_updates:
        return get_exception_by_id(exception_id)
    fields = [f"{key} = ?" for key in safe_updates]
    values = list(safe_updates.values()) + [exception_id]
    with _connect(DB_PATH) as conn:
        conn.execute(f"UPDATE exceptions SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
        conn.commit()
    return get_exception_by_id(exception_id)


def get_all_memories() -> List[dict]:
    with _connect(HINDSIGHT_DB_PATH) as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM memories ORDER BY created_at DESC, id DESC").fetchall()]


def get_memories_by_vendor(vendor: str) -> List[dict]:
    with _connect(HINDSIGHT_DB_PATH) as conn:
        rows = conn.execute("SELECT * FROM memories WHERE lower(vendor) = lower(?) ORDER BY created_at DESC, id DESC", (vendor.strip(),)).fetchall()
        return [dict(row) for row in rows]


def search_memories(vendor: str, problem_type: str, amount_difference: float, limit: int = 5) -> List[dict]:
    """Rank local memories by vendor, problem type, amount proximity and successful outcome."""
    memories = get_all_memories()
    target_vendor = vendor.strip().lower()
    target_type = problem_type.strip().lower()
    target_amount = abs(float(amount_difference or 0))
    ranked = []
    for memory in memories:
        score = 0.0
        if memory['vendor'].strip().lower() == target_vendor:
            score += 0.45
        if memory['problem_type'].strip().lower() == target_type:
            score += 0.30
        elif target_type and target_type in memory['problem_type'].strip().lower():
            score += 0.15
        previous = abs(float(memory.get('amount_difference') or 0))
        denominator = max(target_amount, previous, 1.0)
        score += 0.20 * max(0.0, 1.0 - abs(target_amount - previous) / denominator)
        if memory.get('outcome') == 'successful':
            score += 0.05
        item = dict(memory)
        item['similarity_score'] = round(min(score, 1.0) * 100, 1)
        ranked.append(item)
    ranked.sort(key=lambda item: item['similarity_score'], reverse=True)
    return [item for item in ranked[:limit] if item['similarity_score'] > 0]


def add_memory(data: dict) -> dict:
    """Persist a resolved case so future investigations can reuse it."""
    with _connect(HINDSIGHT_DB_PATH) as conn:
        cursor = conn.execute("""
            INSERT INTO memories (vendor, problem_type, amount_difference, root_cause, solution, outcome)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data['vendor'].strip(), data['problem_type'].strip(), float(data.get('amount_difference', 0) or 0),
            data.get('root_cause', '').strip(), data.get('solution', '').strip(), data['outcome'].strip()
        ))
        conn.commit()
        row = conn.execute("SELECT * FROM memories WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return dict(row)


init_database()
init_hindsight_db()
