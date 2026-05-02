-- ============================================================
--  PhoneBook Extended — Schema Migration (Practice 9)
--  Run this ONCE to migrate from the Practice 8 phonebook table.
-- ============================================================

-- Remove old single-phone table if it still exists
DROP TABLE IF EXISTS phonebook CASCADE;

-- ── 1. Groups / categories ────────────────────────────────────
CREATE TABLE IF NOT EXISTS groups (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Pre-populate the four standard groups
INSERT INTO groups(name)
VALUES ('Family'), ('Work'), ('Friend'), ('Other')
ON CONFLICT DO NOTHING;

-- ── 2. Contacts ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS contacts (
    id         SERIAL       PRIMARY KEY,
    name       VARCHAR(255) NOT NULL UNIQUE,
    email      VARCHAR(100),
    birthday   DATE,
    group_id   INTEGER      REFERENCES groups(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ── 3. Phones (1-to-many) ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS phones (
    id         SERIAL      PRIMARY KEY,
    contact_id INTEGER     NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    phone      VARCHAR(20) NOT NULL,
    type       VARCHAR(10) NOT NULL DEFAULT 'mobile'
                           CHECK (type IN ('home', 'work', 'mobile')),
    UNIQUE (contact_id, phone)
);

-- Handy indexes
CREATE INDEX IF NOT EXISTS idx_contacts_group ON contacts(group_id);
CREATE INDEX IF NOT EXISTS idx_phones_contact ON phones(contact_id);
