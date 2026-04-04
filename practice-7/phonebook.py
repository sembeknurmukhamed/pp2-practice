import csv
import psycopg2
from config import host, user, password, db_name

# ─── Connection ───────────────────────────────────────────────
def get_connection():
    conn = psycopg2.connect(
        host=host, user=user, password=password, database=db_name,
        options="-c client_encoding=UTF8"
    )
    conn.autocommit = True
    return conn

# ─── 1. Create table ──────────────────────────────────────────
def create_table():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS phonebook(
                    id           SERIAL PRIMARY KEY,
                    name         VARCHAR(255) NOT NULL,
                    phone_number VARCHAR(255) UNIQUE NOT NULL
                )
            """)
    print("[INFO] Table is ready")

# ─── 2. Insert from CSV ───────────────────────────────────────
def insert_from_csv(filepath):
    inserted = 0
    skipped  = 0
    conn = get_connection()
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name  = row["name"].strip()
            phone = row["phone_number"].strip()
            if not name or not phone:
                skipped += 1
                continue
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO phonebook(name, phone_number) VALUES(%s, %s)",
                        (name, phone)
                    )
                inserted += 1
            except psycopg2.errors.UniqueViolation:
                print(f"[SKIP] Duplicate phone: {phone}")
                skipped += 1
    conn.close()
    print(f"[INFO] CSV import done — inserted: {inserted}, skipped: {skipped}")

# ─── 3. Insert from console ───────────────────────────────────
def insert_from_console():
    name  = input("Enter name  : ").strip()
    phone = input("Enter phone : ").strip()

    if not name or not phone:
        print("[ERROR] Name and phone cannot be empty")
        return

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO phonebook(name, phone_number) VALUES(%s, %s) RETURNING id",
                (name, phone)
            )
            new_id = cursor.fetchone()[0]
        conn.close()
        print(f"[INFO] Contact added with id={new_id}")
    except psycopg2.errors.UniqueViolation:
        print(f"[ERROR] Phone '{phone}' already exists")

# ─── 4. Update contact ────────────────────────────────────────
def update_contact():
    print("What to search by?")
    print("  1) Name")
    print("  2) Phone number")
    choice = input("Choose [1/2]: ").strip()

    if choice == "1":
        search = input("Enter current name: ").strip()
        field  = "name"
    elif choice == "2":
        search = input("Enter current phone: ").strip()
        field  = "phone_number"
    else:
        print("[ERROR] Invalid choice")
        return

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            f"SELECT id, name, phone_number FROM phonebook WHERE {field} = %s",
            (search,)
        )
        row = cursor.fetchone()

    if not row:
        print("[INFO] Contact not found")
        conn.close()
        return

    cid, cur_name, cur_phone = row
    print(f"\nFound: {cur_name} — {cur_phone}")
    print("Press Enter to keep current value.\n")

    new_name  = input(f"New name  [{cur_name}] : ").strip() or cur_name
    new_phone = input(f"New phone [{cur_phone}]: ").strip() or cur_phone

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE phonebook SET name=%s, phone_number=%s WHERE id=%s",
                (new_name, new_phone, cid)
            )
        print("[INFO] Contact updated successfully")
    except psycopg2.errors.UniqueViolation:
        print(f"[ERROR] Phone '{new_phone}' already belongs to another contact")
    finally:
        conn.close()

# ─── 5. Query / Search ────────────────────────────────────────
def query_contacts():
    print("\nFilter options:")
    print("  1) Show all")
    print("  2) By name")
    print("  3) By phone prefix")
    choice = input("Choose [1/2/3]: ").strip()

    conn = get_connection()
    with conn.cursor() as cursor:
        if choice == "1":
            cursor.execute("SELECT id, name, phone_number FROM phonebook ORDER BY name")

        elif choice == "2":
            name = input("Enter name (partial): ").strip()
            cursor.execute(
                "SELECT id, name, phone_number FROM phonebook WHERE name ILIKE %s ORDER BY name",
                (f"%{name}%",)
            )

        elif choice == "3":
            prefix = input("Enter phone prefix: ").strip()
            cursor.execute(
                "SELECT id, name, phone_number FROM phonebook WHERE phone_number LIKE %s ORDER BY name",
                (f"{prefix}%",)
            )

        else:
            print("[ERROR] Invalid choice")
            conn.close()
            return

        rows = cursor.fetchall()

    conn.close()

    if not rows:
        print("[INFO] No contacts found")
        return

    print(f"\n{'ID':<5} {'Name':<20} {'Phone':<20}")
    print("-" * 45)
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<20} {row[2]:<20}")
    print(f"\nTotal: {len(rows)} contact(s)")

# ─── 6. Delete contact ────────────────────────────────────────
def delete_contact():
    print("Delete by:")
    print("  1) Name")
    print("  2) Phone number")
    choice = input("Choose [1/2]: ").strip()

    if choice == "1":
        value = input("Enter name  : ").strip()
        field = "name"
    elif choice == "2":
        value = input("Enter phone : ").strip()
        field = "phone_number"
    else:
        print("[ERROR] Invalid choice")
        return

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            f"DELETE FROM phonebook WHERE {field} = %s RETURNING name, phone_number",
            (value,)
        )
        deleted = cursor.fetchone()
    conn.close()

    if deleted:
        print(f"[INFO] Deleted: {deleted[0]} — {deleted[1]}")
    else:
        print("[INFO] Contact not found")

# ─── Menu ─────────────────────────────────────────────────────
def main():
    create_table()

    menu = """
╔══════════════════════════════════════╗
║         📞  PhoneBook                ║
╠══════════════════════════════════════╣
║  1. Import from CSV                  ║
║  2. Add contact (console)            ║
║  3. Update contact                   ║
║  4. Search contacts                  ║
║  5. Delete contact                   ║
║  0. Exit                             ║
╚══════════════════════════════════════╝"""

    actions = {
        "1": lambda: insert_from_csv(
            input("CSV path [contacts.csv]: ").strip() or "contacts.csv"
        ),
        "2": insert_from_console,
        "3": update_contact,
        "4": query_contacts,
        "5": delete_contact,
    }

    while True:
        print(menu)
        choice = input("Your choice: ").strip()
        if choice == "0":
            print("Goodbye! 👋")
            break
        elif choice in actions:
            try:
                actions[choice]()
            except Exception as e:
                print(f"[ERROR] {e}")
        else:
            print("[ERROR] Unknown option")

if __name__ == "__main__":
    main()