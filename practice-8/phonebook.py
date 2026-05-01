import csv
import psycopg2
from connect import get_connection


# ──────────────────────────────────────────────
# Table setup
# ──────────────────────────────────────────────

def create_table():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS phonebook(
                    id           SERIAL PRIMARY KEY,
                    name         VARCHAR(255) NOT NULL,
                    phone_number VARCHAR(255) UNIQUE NOT NULL
                )
            """)
    print("[INFO] Table is ready")


# ──────────────────────────────────────────────
# CSV import (unchanged helper)
# ──────────────────────────────────────────────

def insert_from_csv(filepath: str):
    inserted = skipped = 0
    conn = get_connection()
    with open(filepath, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name  = row["name"].strip()
            phone = row["phone_number"].strip()
            if not name or not phone:
                skipped += 1
                continue
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO phonebook(name, phone_number) VALUES(%s, %s)",
                        (name, phone),
                    )
                inserted += 1
            except psycopg2.errors.UniqueViolation:
                print(f"[SKIP] Duplicate phone: {phone}")
                skipped += 1
    conn.close()
    print(f"[INFO] CSV import done — inserted: {inserted}, skipped: {skipped}")


# ──────────────────────────────────────────────
# 1. Search by pattern  →  search_contacts(pattern)
# ──────────────────────────────────────────────

def search_contacts():
    pattern = input("Enter search pattern (name or phone): ").strip()
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
        rows = cur.fetchall()
    conn.close()

    if not rows:
        print("[INFO] No contacts found")
        return

    print(f"\n{'ID':<5} {'Name':<20} {'Phone':<20}")
    print("-" * 45)
    for r in rows:
        print(f"{r[0]:<5} {r[1]:<20} {r[2]:<20}")
    print(f"\nTotal: {len(rows)} contact(s)")


# ──────────────────────────────────────────────
# 2. Upsert single contact  →  upsert_contact(name, phone)
# ──────────────────────────────────────────────

def upsert_contact():
    name  = input("Enter name  : ").strip()
    phone = input("Enter phone : ").strip()
    if not name or not phone:
        print("[ERROR] Name and phone cannot be empty")
        return

    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("CALL upsert_contact(%s, %s)", (name, phone))
    conn.close()
    print("[INFO] Done (inserted or updated)")


# ──────────────────────────────────────────────
# 3. Bulk insert  →  insert_many_contacts(names[], phones[])
# ──────────────────────────────────────────────

def insert_many_contacts():
    print("Enter contacts one per line as  name,phone  (empty line to finish):")
    names, phones = [], []
    while True:
        line = input("  > ").strip()
        if not line:
            break
        parts = line.split(",", 1)
        if len(parts) != 2:
            print("  [WARN] Skipping malformed line (expected name,phone)")
            continue
        names.append(parts[0].strip())
        phones.append(parts[1].strip())

    if not names:
        print("[INFO] Nothing to insert")
        return

    conn = get_connection()
    with conn.cursor() as cur:
        # The procedure has an OUT param — psycopg2 returns it as a result row
        cur.execute(
            "CALL insert_many_contacts(%s, %s, NULL)",
            (names, phones),
        )
        result = cur.fetchone()
    conn.close()

    invalid = result[0] if result else "None"
    print(f"[INFO] Bulk insert done")
    print(f"[INFO] Invalid entries: {invalid}")


# ──────────────────────────────────────────────
# 4. Paginated query  →  get_contacts_page(limit, offset)
# ──────────────────────────────────────────────

def query_paginated():
    try:
        page_size = int(input("Page size [10]: ").strip() or "10")
        page_num  = int(input("Page number (1-based) [1]: ").strip() or "1")
    except ValueError:
        print("[ERROR] Please enter valid integers")
        return

    offset = (page_num - 1) * page_size
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM get_contacts_page(%s, %s)", (page_size, offset))
        rows = cur.fetchall()
    conn.close()

    if not rows:
        print("[INFO] No contacts on this page")
        return

    print(f"\nPage {page_num}  (rows {offset + 1}–{offset + len(rows)})")
    print(f"{'ID':<5} {'Name':<20} {'Phone':<20}")
    print("-" * 45)
    for r in rows:
        print(f"{r[0]:<5} {r[1]:<20} {r[2]:<20}")


# ──────────────────────────────────────────────
# 5. Delete  →  delete_contact(username, phone)
# ──────────────────────────────────────────────

def delete_contact():
    print("Delete by:")
    print("  1) Name")
    print("  2) Phone number")
    choice = input("Choose [1/2]: ").strip()

    conn = get_connection()
    with conn.cursor() as cur:
        if choice == "1":
            value = input("Enter name  : ").strip()
            cur.execute("CALL delete_contact(p_username := %s)", (value,))
        elif choice == "2":
            value = input("Enter phone : ").strip()
            cur.execute("CALL delete_contact(p_phone := %s)", (value,))
        else:
            print("[ERROR] Invalid choice")
            conn.close()
            return
    conn.close()
    print("[INFO] Done")


# ──────────────────────────────────────────────
# Main menu
# ──────────────────────────────────────────────

MENU = """
╔══════════════════════════════════════════╗
║          📞  PhoneBook  (Practice 8)     ║
╠══════════════════════════════════════════╣
║  1. Import from CSV                      ║
║  2. Upsert contact (insert or update)    ║
║  3. Bulk insert from console             ║
║  4. Search by pattern                    ║
║  5. Browse with pagination               ║
║  6. Delete contact                       ║
║  0. Exit                                 ║
╚══════════════════════════════════════════╝"""

ACTIONS = {
    "1": lambda: insert_from_csv(
        input("CSV path [contacts.csv]: ").strip() or "contacts.csv"
    ),
    "2": upsert_contact,
    "3": insert_many_contacts,
    "4": search_contacts,
    "5": query_paginated,
    "6": delete_contact,
}


def main():
    create_table()
    while True:
        print(MENU)
        choice = input("Your choice: ").strip()
        if choice == "0":
            print("Goodbye! 👋")
            break
        elif choice in ACTIONS:
            try:
                ACTIONS[choice]()
            except Exception as e:
                print(f"[ERROR] {e}")
        else:
            print("[ERROR] Unknown option")


if __name__ == "__main__":
    main()
