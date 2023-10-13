CREATE OR REPLACE FUNCTION encrypt_array(arr TEXT[], key TEXT)
RETURNS BYTEA[] AS $$
DECLARE
  result BYTEA[];
BEGIN
  SELECT ARRAY(
    SELECT pgp_sym_encrypt(element, key) AS encrypted_element
    FROM unnest(arr) AS element
  ) INTO result;

  RETURN result;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION decrypt_array(arr bytea[], key TEXT)
RETURNS TEXT[] AS $$
DECLARE
  result TEXT[];
BEGIN
  SELECT array_agg(pgp_sym_decrypt(element, key)) INTO result
  FROM unnest(arr) AS element;

  RETURN result;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION remove_encrypted_array_element(value TEXT, arr bytea[], key TEXT)
RETURNS bytea[] AS $$
DECLARE
  result bytea[];
BEGIN
  SELECT ARRAY(
    SELECT pgp_sym_encrypt(decrypted_element, key) AS reencrypted_element
    FROM (
      SELECT pgp_sym_decrypt(element, key) AS decrypted_element
      FROM unnest(arr) AS element
      WHERE pgp_sym_decrypt(element, key) <> value
    ) AS subquery
  ) INTO result;

  RETURN result;
END;
$$ LANGUAGE plpgsql;
