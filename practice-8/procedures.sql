-- ============================================================
--  PhoneBook — SQL PROCEDURES  (Practice 8)
-- ============================================================

-- 2. Upsert a single contact:
--    insert if name is new, otherwise update their phone number.
CREATE OR REPLACE PROCEDURE upsert_contact(
    p_name  VARCHAR,
    p_phone VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phonebook WHERE name = p_name) THEN
        UPDATE phonebook
        SET    phone_number = p_phone
        WHERE  name = p_name;
        RAISE NOTICE '[UPDATE] % → %', p_name, p_phone;
    ELSE
        INSERT INTO phonebook(name, phone_number)
        VALUES (p_name, p_phone);
        RAISE NOTICE '[INSERT] % — %', p_name, p_phone;
    END IF;
END;
$$;

-- Usage:
--   CALL upsert_contact('Alice', '+77001112233');


-- ============================================================
-- 3. Bulk insert from parallel arrays.
--    Validates each phone with a regex.
--    OUT parameter invalid_entries holds every rejected row.
-- ============================================================
CREATE OR REPLACE PROCEDURE insert_many_contacts(
    p_names   TEXT[],
    p_phones  TEXT[],
    OUT invalid_entries TEXT        -- returned to the caller
)
LANGUAGE plpgsql AS $$
DECLARE
    i       INT;
    p_name  TEXT;
    p_phone TEXT;
    bad     TEXT[] := '{}';
BEGIN
    -- Guard: arrays must be the same length
    IF array_length(p_names, 1) IS DISTINCT FROM array_length(p_phones, 1) THEN
        RAISE EXCEPTION 'Names and phones arrays must have equal length';
    END IF;

    FOR i IN 1 .. array_length(p_names, 1) LOOP
        p_name  := TRIM(p_names[i]);
        p_phone := TRIM(p_phones[i]);

        -- Validate: optional leading +, then 10-15 digits, nothing else
        IF p_phone !~ '^\+?[0-9]{10,15}$' THEN
            bad := array_append(bad, p_name || ' | ' || p_phone);
            RAISE NOTICE '[INVALID] % — bad phone: %', p_name, p_phone;
            CONTINUE;
        END IF;

        -- Upsert
        IF EXISTS (SELECT 1 FROM phonebook WHERE name = p_name) THEN
            UPDATE phonebook
            SET    phone_number = p_phone
            WHERE  name = p_name;
        ELSE
            INSERT INTO phonebook(name, phone_number)
            VALUES (p_name, p_phone);
        END IF;
    END LOOP;

    -- Build the OUT value
    IF array_length(bad, 1) IS NULL THEN
        invalid_entries := 'None';
    ELSE
        invalid_entries := array_to_string(bad, ' | ');
    END IF;
END;
$$;

-- Usage:
--   CALL insert_many_contacts(
--       ARRAY['Bob', 'Eve', 'BadGuy'],
--       ARRAY['+77771234567', '+77779876543', 'not-a-phone'],
--       NULL
--   );


-- ============================================================
-- 5. Delete a contact by username OR phone number.
--    Exactly one of the two parameters must be provided.
-- ============================================================
CREATE OR REPLACE PROCEDURE delete_contact(
    p_username VARCHAR DEFAULT NULL,
    p_phone    VARCHAR DEFAULT NULL
)
LANGUAGE plpgsql AS $$
DECLARE
    del_name  VARCHAR;
    del_phone VARCHAR;
BEGIN
    IF p_username IS NOT NULL THEN
        DELETE FROM phonebook
        WHERE  name = p_username
        RETURNING name, phone_number
        INTO del_name, del_phone;

    ELSIF p_phone IS NOT NULL THEN
        DELETE FROM phonebook
        WHERE  phone_number = p_phone
        RETURNING name, phone_number
        INTO del_name, del_phone;

    ELSE
        RAISE EXCEPTION 'Provide either p_username or p_phone';
    END IF;

    IF del_name IS NOT NULL THEN
        RAISE NOTICE '[DELETED] % — %', del_name, del_phone;
    ELSE
        RAISE NOTICE '[NOT FOUND] No matching contact';
    END IF;
END;
$$;

-- Usage:
--   CALL delete_contact(p_username := 'Alice');
--   CALL delete_contact(p_phone    := '+77001112233');
