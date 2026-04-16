# Encryption

`envpatch` supports symmetric encryption of `.env` values using [Fernet](https://cryptography.io/en/latest/fernet/) (AES-128-CBC + HMAC).

## Installation

Install the optional dependency:

```bash
pip install envpatch[crypto]
```

## Generate a key

```bash
envpatch encrypt keygen
# outputs: <base64-fernet-key>
export ENVPATCH_KEY=<key>
```

Store the key securely (e.g. in a secrets manager). **Never commit it.**

## Encrypt values

Encrypt all values in a file:

```bash
envpatch encrypt encrypt .env --key $ENVPATCH_KEY -o .env.enc
```

Encrypt only specific keys:

```bash
envpatch encrypt encrypt .env --key $ENVPATCH_KEY --only DB_PASSWORD --only API_KEY
```

## Decrypt values

```bash
envpatch encrypt decrypt .env.enc --key $ENVPATCH_KEY
```

## Notes

- Non-targeted keys are passed through unchanged when using `--only`.
- Decryption emits a warning for any key whose value could not be decrypted (e.g. plaintext values mixed in).
- The `ENVPATCH_KEY` environment variable is read automatically if `--key` is not provided.
