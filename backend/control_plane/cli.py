"""Küçük yönetim CLI'ı — control-plane.

Parolayı ``getpass`` ile sorar (ekrana/loga yazılmaz, .env'e plaintext girmez).

Kullanım:
    PYTHONPATH=. .venv/bin/python -m control_plane.cli create-superadmin --email root@dima.co
    # parola interaktif sorulur

Non-interaktif (CI vb.):
    ... create-superadmin --email x@y.co --password '...'
"""

from __future__ import annotations

import argparse
import getpass
import sys

from sqlmodel import Session, select

from control_plane.db import engine, init_db
from control_plane.models import User
from control_plane.security import hash_password, totp_secret, totp_uri
from control_plane.seed import seed_demo


def create_superadmin(email: str | None, password: str | None) -> int:
    init_db()  # SQLite'ta tabloları oluşturur; Postgres'te Alembic hallettiği için no-op.
    email = (email or input("E-posta: ")).strip()
    if not email:
        print("E-posta boş olamaz.")
        return 1
    if not password:
        password = getpass.getpass("Parola: ")
        if password != getpass.getpass("Parola (tekrar): "):
            print("Parolalar uyuşmuyor.")
            return 1
    if len(password) < 8:
        print("Parola en az 8 karakter olmalı.")
        return 1
    with Session(engine) as session:
        if session.exec(select(User).where(User.email == email)).first():
            print(f"Bu e-posta zaten kayıtlı: {email}")
            return 1
        session.add(User(email=email, password_hash=hash_password(password),
                         is_superadmin=True))
        session.commit()
    print(f"Superadmin oluşturuldu: {email}  (backend: {engine.url.get_backend_name()})")
    return 0


def enroll_mfa(email: str | None) -> int:
    """TOTP secret'ı üretir, kullanıcıya yazar ve authenticator URI'ını basar.

    ADR-0015: superadmin'de 2FA zorunlu — prod'a çıkmadan her superadmin bu komutla
    enroll edilir, sonra DIMA_REQUIRE_SUPERADMIN_MFA=true açılır.
    """
    init_db()
    email = (email or input("E-posta: ")).strip()
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if not user:
            print(f"Kullanıcı bulunamadı: {email}")
            return 1
        secret = totp_secret()
        user.mfa_secret = secret
        session.add(user)
        session.commit()
    print("TOTP secret kaydedildi. Authenticator uygulamasına ekleyin:")
    print(f"  {totp_uri(secret, email)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="control_plane.cli")
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("create-superadmin", help="Yeni platform superadmin'i oluştur")
    c.add_argument("--email", default=None)
    c.add_argument("--password", default=None, help="Verilmezse getpass ile sorulur")
    m = sub.add_parser("enroll-mfa", help="Kullanıcıya TOTP (2FA) secret'ı ata")
    m.add_argument("--email", default=None)
    sub.add_parser("seed-demo", help="Lokal demo fixture: 2 firma + owner kullanıcıları")
    args = parser.parse_args(argv)
    if args.cmd == "create-superadmin":
        return create_superadmin(args.email, args.password)
    if args.cmd == "enroll-mfa":
        return enroll_mfa(args.email)
    if args.cmd == "seed-demo":
        return seed_demo()
    return 2


if __name__ == "__main__":
    sys.exit(main())
