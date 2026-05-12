import sqlite3
from datetime import datetime
from config import DB_NAME, ROOMS


def get_connection():
    """Get database connection with row factory."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables and insert room data."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create rooms table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            code TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            price INTEGER NOT NULL
        )
    """)

    # Create bookings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guest_name TEXT NOT NULL,
            room_code TEXT NOT NULL,
            check_in TEXT NOT NULL,
            check_out TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            FOREIGN KEY (room_code) REFERENCES rooms(code)
        )
    """)

    # Insert room data (replace if exists)
    for room in ROOMS:
        cursor.execute("""
            INSERT OR REPLACE INTO rooms (code, type, price)
            VALUES (?, ?, ?)
        """, (room["code"], room["type"], room["price"]))

    conn.commit()
    conn.close()
    print(f"Database initialized: {DB_NAME}")


def get_available_rooms(check_in, check_out):
    """Return list of available room codes for given date range."""
    conn = get_connection()
    cursor = conn.cursor()

    # Find rooms that are NOT booked (overlapping dates) with pending/confirmed status
    cursor.execute("""
        SELECT code FROM rooms
        WHERE code NOT IN (
            SELECT room_code FROM bookings
            WHERE status IN ('pending', 'confirmed')
            AND check_in < ?
            AND check_out > ?
        )
        ORDER BY code
    """, (check_out, check_in))

    available = [row["code"] for row in cursor.fetchall()]
    conn.close()
    return available


def add_booking(guest_name, room_code, check_in, check_out):
    """Add new booking, return booking_id."""
    conn = get_connection()
    cursor = conn.cursor()

    created_at = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO bookings (guest_name, room_code, check_in, check_out, status, created_at)
        VALUES (?, ?, ?, ?, 'pending', ?)
    """, (guest_name, room_code, check_in, check_out, created_at))

    booking_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return booking_id


def get_pending_booking_by_guest(guest_name):
    """Find pending booking by guest name."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, guest_name, room_code, check_in, check_out, status, created_at
        FROM bookings
        WHERE LOWER(guest_name) = LOWER(?) AND status = 'pending'
        ORDER BY created_at DESC
        LIMIT 1
    """, (guest_name,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def confirm_booking(booking_id):
    """Update booking status to 'confirmed'. Returns True if successful."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE bookings
        SET status = 'confirmed'
        WHERE id = ? AND status = 'pending'
    """, (booking_id,))

    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success


def cancel_booking(booking_id):
    """Update booking status to 'cancelled'. Returns True if successful."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE bookings
        SET status = 'cancelled'
        WHERE id = ?
    """, (booking_id,))

    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success


if __name__ == "__main__":
    init_db()