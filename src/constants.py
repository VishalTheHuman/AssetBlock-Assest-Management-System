DESCRIPTION_MARKDOWN = """**:red[Asset]:orange[Block]** is a cutting-edge platform revolutionizing asset management through the power of blockchain technology. With **:red[Asset]:orange[Block]**, users can **:blue[track], :blue[transfer], and :blue[trade] assets** seamlessly, unlocking new levels of accessibility and liquidity."""

STATUS_ENUM = """
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_enum') THEN
        CREATE TYPE status_enum AS ENUM ('Accepted', 'Under Review', 'Rejected');
    END IF;
END$$;
"""

FILE_TYPE_ENUM = """
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'file_type_enum') THEN
        CREATE TYPE file_type_enum AS ENUM ('Document', 'Certificate', 'License');
    END IF;
END$$;
"""

ASSET_DATA_SCHEMA = """
CREATE TABLE ASSET_DATA (
    uid VARCHAR(100),
    email VARCHAR(255),
    hashvalue VARCHAR(255) PRIMARY KEY,
    filename VARCHAR(255),
    file BYTEA,
    status status_enum,
    date DATE,
    time TIME WITHOUT TIME ZONE,
    file_type file_type_enum
);
"""

INSERT_QUERY = """
INSERT INTO ASSET_DATA (uid, email, hashvalue, filename, file, status, date, time, file_type)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
"""