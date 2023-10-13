-- select decrypted email addresses array
SELECT array_agg(pgp_sym_decrypt(element::bytea, 'key')) AS gmail_email_addresses
FROM accounts, unnest(accounts.gmail_email_addresses) AS element
GROUP BY accounts.account_id;

-- with functions
SELECT decrypt_array(gmail_email_addresses, 'key') FROM accounts;




-- insert row with email addresses
INSERT INTO accounts (gmail_email_addresses)
VALUES (ARRAY(
  -- Encrypt the elements of the new array
  SELECT pgp_sym_encrypt(element, 'key') AS encrypted_element
  FROM unnest(ARRAY['foo', 'bar']) AS element
));

-- with functions
INSERT INTO accounts (gmail_email_addresses)
VALUES (encrypt_array(ARRAY['foo', 'bar'], 'key'));




-- update email addresses with dynamically sized list
UPDATE accounts
SET gmail_email_addresses = ARRAY(
  -- Encrypt the elements of the new array
  SELECT pgp_sym_encrypt(element, 'key') AS encrypted_element
  FROM unnest(ARRAY['foo', 'bar']) AS element
);

-- with functions
UPDATE accounts
SET gmail_email_addresses = encrypt_array(ARRAY['foo', 'bar'], 'key');




-- remove email address from array
UPDATE accounts
SET gmail_email_addresses = ARRAY(
  -- Re-encrypt the decrypted elements
  SELECT pgp_sym_encrypt(decrypted_element, 'key') AS reencrypted_element
  FROM (
    -- Decrypt the elements and filter out the 'baz' value
    SELECT pgp_sym_decrypt(element, 'key') AS decrypted_element
    FROM accounts, unnest(accounts.gmail_email_addresses) AS element
    WHERE pgp_sym_decrypt(element, 'key') <> 'baz'
  ) AS subquery
);

-- with functions
UPDATE accounts
SET gmail_email_addresses =
    remove_encrypted_array_element('foo', gmail_email_addresses, 'key');




-- append email address to list
UPDATE accounts
SET gmail_email_addresses =
  gmail_email_addresses || pgp_sym_encrypt('baz', 'key');
