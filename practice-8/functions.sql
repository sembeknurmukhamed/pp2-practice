-- ============================================================
--  PhoneBook — SQL FUNCTIONS  (Practice 8)
-- ============================================================

-- 1. Search contacts by pattern (name OR phone, case-insensitive)
CREATE OR REPLACE FUNCTION search_contacts(pattern TEXT)
RETURNS TABLE(id INT, name VARCHAR, phone_number VARCHAR) AS $$
BEGIN
    RETURN QUERY
        SELECT p.id, p.name, p.phone_number
        FROM   phonebook p
        WHERE  p.name         ILIKE '%' || pattern || '%'
            OR p.phone_number ILIKE '%' || pattern || '%'
        ORDER  BY p.name;
END;
$$ LANGUAGE plpgsql;

-- Usage:
--   SELECT * FROM search_contacts('Ali');
--   SELECT * FROM search_contacts('+7701');


-- 4. Paginated query  (page starts at 0)
CREATE OR REPLACE FUNCTION get_contacts_page(
    page_limit  INT,
    page_offset INT
)
RETURNS TABLE(id INT, name VARCHAR, phone_number VARCHAR) AS $$
BEGIN
    RETURN QUERY
        SELECT p.id, p.name, p.phone_number
        FROM   phonebook p
        ORDER  BY p.name
        LIMIT  page_limit
        OFFSET page_offset;
END;
$$ LANGUAGE plpgsql;

-- Usage:
--   SELECT * FROM get_contacts_page(10, 0);   -- page 1
--   SELECT * FROM get_contacts_page(10, 10);  -- page 2
