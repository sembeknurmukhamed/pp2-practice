"""
phonebook.py — Extended PhoneBook (Practice 9)
Requires: schema.sql + procedures_v2.sql applied to the DB first.
"""

import csv
import json
import psycopg2
from datetime import date, datetime
from connect import get_connection

# ═══════════════════════════════════════════════════════════════
# TABLE SETUP
# ═══════════════════════════════════════════════════════════════

def create_tables():
    """Idempotently create groups / contacts / phones tables."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                id   SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL
            )
        """)
        cur.execute("""
            INSERT INTO groups(name)
            VALUES ('Family'),('Work'),('Friend'),('Other')
            ON CONFLICT DO NOTHING
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id         SERIAL       PRIMARY KEY,
                name       VARCHAR(255) NOT NULL UNIQUE,
                email      VARCHAR(100),
                birthday   DATE,
                group_id   INTEGER      REFERENCES groups(id) ON DELETE SET NULL,
                created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS phones (
                id         SERIAL      PRIMARY KEY,
                contact_id INTEGER     NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
                phone      VARCHAR(20) NOT NULL,
                type       VARCHAR(10) NOT NULL DEFAULT 'mobile'
                           CHECK (type IN ('home','work','mobile')),
                UNIQUE (contact_id, phone)
            )
        """)
    conn.close()
    print("[INFO] Tables are ready")


# ═══════════════════════════════════════════════════════════════
# DISPLAY HELPERS
# ═══════════════════════════════════════════════════════════════

_COL_W = {"id": 5, "name": 22, "email": 26, "birthday": 12,
           "group": 10, "phones": 30}

def _header():
    return (
        f"{'ID':<{_COL_W['id']}} "
        f"{'Name':<{_COL_W['name']}} "
        f"{'Email':<{_COL_W['email']}} "
        f"{'Birthday':<{_COL_W['birthday']}} "
        f"{'Group':<{_COL_W['group']}} "
        f"Phones"
    )

def _row_str(r):
    cid, name, email, bday, grp, phones, *_ = r
    return (
        f"{cid:<{_COL_W['id']}} "
        f"{(name or ''):<{_COL_W['name']}} "
        f"{(email or ''):<{_COL_W['email']}} "
        f"{(str(bday) if bday else ''):<{_COL_W['birthday']}} "
        f"{(grp or ''):<{_COL_W['group']}} "
        f"{phones or ''}"
    )

def _print_contacts(rows, *, label=""):
    if not rows:
        print("[INFO] No contacts found")
        return
    if label:
        print(f"\n  {label}")
    print(f"\n{_header()}")
    print("─" * 100)
    for r in rows:
        print(_row_str(r))
    print(f"\nTotal: {len(rows)} contact(s)")


def _pick_sort() -> str:
    print("\nSort by:")
    print("  1) Name (default)")
    print("  2) Birthday")
    print("  3) Date added")
    choice = input("  Choose [1]: ").strip() or "1"
    return {"1": "name", "2": "birthday", "3": "created_at"}.get(choice, "name")


def _pick_type(prompt="Phone type") -> str:
    print(f"{prompt}:  1) mobile (default)  2) home  3) work")
    choice = input("  Choose [1]: ").strip() or "1"
    return {"1": "mobile", "2": "home", "3": "work"}.get(choice, "mobile")


def _list_groups() -> list[tuple]:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM groups ORDER BY name")
        rows = cur.fetchall()
    conn.close()
    return rows


# ═══════════════════════════════════════════════════════════════
# 1. IMPORT FROM CSV  (extended: email, birthday, group, type)
# ═══════════════════════════════════════════════════════════════
# Expected CSV columns:
#   name, phone [, phone_type, email, birthday (YYYY-MM-DD), group]

def insert_from_csv(filepath: str):
    inserted = skipped = 0
    conn = get_connection()
    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=2):          # row 1 = header
                name  = row.get("name", "").strip()
                phone = row.get("phone", "").strip()
                if not name or not phone:
                    print(f"  [WARN] Row {i}: missing name or phone — skipped")
                    skipped += 1
                    continue

                p_type    = (row.get("phone_type") or "mobile").strip()
                email     = row.get("email", "").strip() or None
                birthday  = row.get("birthday", "").strip() or None
                group_name = row.get("group", "").strip() or None

                if p_type not in ("home", "work", "mobile"):
                    p_type = "mobile"

                try:
                    with conn.cursor() as cur:
                        cur.execute(
                            "CALL upsert_contact(%s, %s, %s, %s, %s, %s)",
                            (name, phone, p_type, email, birthday, group_name),
                        )
                    inserted += 1
                except Exception as e:
                    print(f"  [WARN] Row {i} ({name}): {e}")
                    skipped += 1
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filepath}")
        conn.close()
        return

    conn.close()
    print(f"[INFO] CSV import done — inserted/updated: {inserted}, skipped: {skipped}")


# ═══════════════════════════════════════════════════════════════
# 2. UPSERT SINGLE CONTACT
# ═══════════════════════════════════════════════════════════════

def upsert_contact():
    name  = input("Name        : ").strip()
    phone = input("Phone       : ").strip()
    if not name or not phone:
        print("[ERROR] Name and phone are required")
        return

    p_type = _pick_type()
    email  = input("Email       (leave blank to skip): ").strip() or None
    bday   = input("Birthday    (YYYY-MM-DD, blank to skip): ").strip() or None

    groups = _list_groups()
    print("\nGroup:")
    for i, (_, g) in enumerate(groups, 1):
        print(f"  {i}) {g}")
    print("  0) None")
    gi = input("  Choose [0]: ").strip()
    group = None
    if gi.isdigit() and 0 < int(gi) <= len(groups):
        group = groups[int(gi) - 1][1]

    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "CALL upsert_contact(%s, %s, %s, %s, %s, %s)",
            (name, phone, p_type, email, bday, group),
        )
    conn.close()
    print("[INFO] Contact saved")


# ═══════════════════════════════════════════════════════════════
# 3. BULK INSERT FROM CONSOLE
# ═══════════════════════════════════════════════════════════════
# Format: name,phone[,type]   (one per line, empty line to finish)

def insert_many_contacts():
    print("Enter contacts — format:  name,phone[,type]")
    print("  type is optional: home | work | mobile (default: mobile)")
    print("  Empty line to finish.\n")
    names, phones, types = [], [], []

    while True:
        line = input("  > ").strip()
        if not line:
            break
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 2:
            print("  [WARN] Need at least name,phone — skipping")
            continue
        names.append(parts[0])
        phones.append(parts[1])
        types.append(parts[2] if len(parts) > 2 else "mobile")

    if not names:
        print("[INFO] Nothing to insert")
        return

    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "CALL insert_many_contacts(%s, %s, %s, NULL)",
            (names, phones, types),
        )
        result = cur.fetchone()
    conn.close()

    invalid = result[0] if result else "None"
    print("[INFO] Bulk insert done")
    print(f"[INFO] Invalid entries: {invalid}")


# ═══════════════════════════════════════════════════════════════
# 4. SEARCH BY PATTERN  (name / email / phone)
# ═══════════════════════════════════════════════════════════════

def search_contacts():
    pattern = input("Search (name / email / phone): ").strip()
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
        rows = cur.fetchall()
    conn.close()
    _print_contacts(rows, label=f'Results for "{pattern}"')


# ═══════════════════════════════════════════════════════════════
# 5. PAGINATED BROWSE  (next / prev / quit navigation)
# ═══════════════════════════════════════════════════════════════

def query_paginated():
    try:
        page_size = int(input("Page size [10]: ").strip() or "10")
    except ValueError:
        print("[ERROR] Invalid number")
        return

    sort_col = _pick_sort()
    page     = 1

    while True:
        offset = (page - 1) * page_size
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM get_contacts_page(%s, %s, %s)",
                (page_size, offset, sort_col),
            )
            rows = cur.fetchall()
        conn.close()

        print(f"\n  ── Page {page} (sorted by {sort_col}) ──")
        _print_contacts(rows)
        has_next = len(rows) == page_size
        has_prev = page > 1

        nav_opts = []
        if has_prev: nav_opts.append("[p]rev")
        if has_next: nav_opts.append("[n]ext")
        nav_opts.append("[q]uit")
        print("\n  " + "  ".join(nav_opts))

        nav = input("  > ").strip().lower()
        if nav == "n":
            if has_next:
                page += 1
            else:
                print("  [INFO] Already on the last page")
        elif nav == "p":
            if has_prev:
                page -= 1
            else:
                print("  [INFO] Already on the first page")
        elif nav == "q":
            break


# ═══════════════════════════════════════════════════════════════
# 6. FILTER BY GROUP
# ═══════════════════════════════════════════════════════════════

def filter_by_group():
    groups = _list_groups()
    if not groups:
        print("[INFO] No groups found")
        return

    print("\nAvailable groups:")
    for i, (_, g) in enumerate(groups, 1):
        print(f"  {i}) {g}")
    gi = input("Choose group: ").strip()
    if not gi.isdigit() or not (1 <= int(gi) <= len(groups)):
        print("[ERROR] Invalid selection")
        return

    group_name = groups[int(gi) - 1][1]
    sort_col   = _pick_sort()

    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT c.id, c.name, c.email, c.birthday, g.name,
                   STRING_AGG(ph.phone || ' [' || COALESCE(ph.type,'?') || ']',
                              ', ' ORDER BY ph.type),
                   c.created_at
            FROM   contacts c
            LEFT JOIN groups g  ON g.id = c.group_id
            LEFT JOIN phones ph ON ph.contact_id = c.id
            WHERE  g.name = %s
            GROUP  BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
            ORDER  BY c.{sort_col} NULLS LAST
            """,
            (group_name,),
        )
        rows = cur.fetchall()
    conn.close()
    _print_contacts(rows, label=f"Group: {group_name}")


# ═══════════════════════════════════════════════════════════════
# 7. SEARCH BY EMAIL
# ═══════════════════════════════════════════════════════════════

def search_by_email():
    pattern = input("Email pattern (e.g. gmail): ").strip()
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT c.id, c.name, c.email, c.birthday, g.name,
                   STRING_AGG(ph.phone || ' [' || COALESCE(ph.type,'?') || ']',
                              ', ' ORDER BY ph.type),
                   c.created_at
            FROM   contacts c
            LEFT JOIN groups g  ON g.id = c.group_id
            LEFT JOIN phones ph ON ph.contact_id = c.id
            WHERE  c.email ILIKE %s
            GROUP  BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
            ORDER  BY c.name
            """,
            (f"%{pattern}%",),
        )
        rows = cur.fetchall()
    conn.close()
    _print_contacts(rows, label=f'Email matching "{pattern}"')


# ═══════════════════════════════════════════════════════════════
# 8. DELETE CONTACT
# ═══════════════════════════════════════════════════════════════

def delete_contact():
    print("\nDelete by:")
    print("  1) Name")
    print("  2) Phone number")
    choice = input("Choose [1/2]: ").strip()

    conn = get_connection()
    with conn.cursor() as cur:
        if choice == "1":
            value = input("Name  : ").strip()
            cur.execute("CALL delete_contact(p_username := %s)", (value,))
        elif choice == "2":
            value = input("Phone : ").strip()
            cur.execute("CALL delete_contact(p_phone := %s)", (value,))
        else:
            print("[ERROR] Invalid choice")
            conn.close()
            return
    conn.close()
    print("[INFO] Done")


# ═══════════════════════════════════════════════════════════════
# 9. ADD PHONE TO EXISTING CONTACT
# ═══════════════════════════════════════════════════════════════

def add_phone_to_contact():
    name  = input("Contact name : ").strip()
    phone = input("New phone    : ").strip()
    if not name or not phone:
        print("[ERROR] Name and phone are required")
        return
    p_type = _pick_type()

    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, p_type))
    conn.close()
    print("[INFO] Phone added")


# ═══════════════════════════════════════════════════════════════
# 10. MOVE CONTACT TO GROUP
# ═══════════════════════════════════════════════════════════════

def move_contact_to_group():
    name = input("Contact name      : ").strip()
    grp  = input("Group name        : ").strip()
    if not name or not grp:
        print("[ERROR] Both fields are required")
        return

    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("CALL move_to_group(%s, %s)", (name, grp))
    conn.close()
    print(f"[INFO] {name} moved to group '{grp}'")


# ═══════════════════════════════════════════════════════════════
# 11. EXPORT TO JSON
# ═══════════════════════════════════════════════════════════════

def _date_serial(obj):
    """JSON serialiser for date / datetime objects."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serialisable")


def export_to_json():
    filepath = input("Output file [contacts.json]: ").strip() or "contacts.json"
    conn = get_connection()
    with conn.cursor() as cur:
        # Fetch contacts
        cur.execute("""
            SELECT c.id, c.name, c.email, c.birthday, g.name AS group_name
            FROM   contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            ORDER  BY c.name
        """)
        contacts_raw = cur.fetchall()

        # Fetch all phones grouped by contact
        cur.execute("""
            SELECT contact_id, phone, type
            FROM   phones
            ORDER  BY contact_id, type
        """)
        phones_raw = cur.fetchall()
    conn.close()

    # Build phones lookup {contact_id: [{phone, type}, ...]}
    phones_map: dict[int, list] = {}
    for cid, phone, ptype in phones_raw:
        phones_map.setdefault(cid, []).append({"phone": phone, "type": ptype})

    result = []
    for cid, name, email, birthday, group_name in contacts_raw:
        result.append({
            "name":     name,
            "email":    email,
            "birthday": birthday,
            "group":    group_name,
            "phones":   phones_map.get(cid, []),
        })

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=_date_serial)

    print(f"[INFO] Exported {len(result)} contact(s) → {filepath}")


# ═══════════════════════════════════════════════════════════════
# 12. IMPORT FROM JSON
# ═══════════════════════════════════════════════════════════════

def import_from_json():
    filepath = input("JSON file [contacts.json]: ").strip() or "contacts.json"
    try:
        with open(filepath, encoding="utf-8") as f:
            records = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filepath}")
        return
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON: {e}")
        return

    inserted = updated = skipped = 0
    conn = get_connection()

    for rec in records:
        name  = (rec.get("name") or "").strip()
        email = rec.get("email")
        bday  = rec.get("birthday")
        group = rec.get("group")
        phones_list = rec.get("phones", [])

        if not name:
            print("  [WARN] Skipping record with no name")
            skipped += 1
            continue

        # Check for duplicate
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
            existing = cur.fetchone()

        if existing:
            choice = input(
                f"  '{name}' already exists — [s]kip / [o]verwrite? [s]: "
            ).strip().lower() or "s"
            if choice != "o":
                skipped += 1
                continue

        # Upsert contact record
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO contacts(name, email, birthday)
                VALUES (%s, %s, %s)
                ON CONFLICT (name) DO UPDATE
                    SET email    = EXCLUDED.email,
                        birthday = EXCLUDED.birthday
                RETURNING id
            """, (name, email or None, bday or None))
            cid = cur.fetchone()[0]

            # Set group
            if group:
                cur.execute("SELECT id FROM groups WHERE name = %s", (group,))
                g_row = cur.fetchone()
                if g_row:
                    cur.execute(
                        "UPDATE contacts SET group_id = %s WHERE id = %s",
                        (g_row[0], cid),
                    )

            # Insert phones
            for p in phones_list:
                ph    = (p.get("phone") or "").strip()
                ptype = (p.get("type")  or "mobile").strip()
                if ph:
                    cur.execute("""
                        INSERT INTO phones(contact_id, phone, type)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (contact_id, phone) DO UPDATE SET type = EXCLUDED.type
                    """, (cid, ph, ptype))

        if existing:
            updated += 1
        else:
            inserted += 1

    conn.close()
    print(f"[INFO] JSON import done — inserted: {inserted}, updated: {updated}, skipped: {skipped}")


# ═══════════════════════════════════════════════════════════════
# MENU
# ═══════════════════════════════════════════════════════════════

MENU = """
╔══════════════════════════════════════════════════════╗
║          📞  PhoneBook Extended  (Practice 9)        ║
╠══════════════════════════════════════════════════════╣
║  Import / Export                                     ║
║    1. Import from CSV                                ║
║   11. Export to JSON                                 ║
║   12. Import from JSON                               ║
╠══════════════════════════════════════════════════════╣
║  Edit                                                ║
║    2. Upsert contact (insert or update)              ║
║    3. Bulk insert from console                       ║
║    8. Delete contact                                 ║
║    9. Add phone to existing contact                  ║
║   10. Move contact to group                          ║
╠══════════════════════════════════════════════════════╣
║  Search & Browse                                     ║
║    4. Search by pattern (name / email / phone)       ║
║    5. Browse with pagination                         ║
║    6. Filter by group                                ║
║    7. Search by email                                ║
╠══════════════════════════════════════════════════════╣
║    0. Exit                                           ║
╚══════════════════════════════════════════════════════╝"""

ACTIONS = {
    "1":  lambda: insert_from_csv(
              input("CSV path [contacts.csv]: ").strip() or "contacts.csv"
          ),
    "2":  upsert_contact,
    "3":  insert_many_contacts,
    "4":  search_contacts,
    "5":  query_paginated,
    "6":  filter_by_group,
    "7":  search_by_email,
    "8":  delete_contact,
    "9":  add_phone_to_contact,
    "10": move_contact_to_group,
    "11": export_to_json,
    "12": import_from_json,
}


def main():
    create_tables()
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
