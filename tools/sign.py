import hashlib
import hmac
import sys


def sign(payload: bytes, secret: str) -> str:
    digest = hmac.new(
        key=secret.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha256,
    ).hexdigest()
    return f"sha256={digest}"


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: sign.py <payload> <secret>", file=sys.stderr)
        sys.exit(2)
    payload = sys.argv[1].encode("utf-8")
    secret = sys.argv[2]
    print(sign(payload, secret))