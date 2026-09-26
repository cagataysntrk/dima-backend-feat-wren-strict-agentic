"""One bounded Resend test-mode live canary.

No CLI inputs. Recipient is hard-locked to Resend's designated delivered test address.
The same candidate SHA always derives the same logical send identity.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from app.config import get_settings
from app.v3.action_connectors.resend_email import (
    ResendEmailConnector,
    ResendEmailRequest,
    ResendSendState,
)

CANARY_RECIPIENT = "delivered@resend.dev"
RECEIPT_PATH = Path("lab/metabase/action_execution/resend-canary-receipt.json")


def main() -> None:
    candidate = os.environ.get("DIMA_RESEND_CANARY_CANDIDATE", "").strip()
    if not candidate:
        raise SystemExit("DIMA_RESEND_CANARY_CANDIDATE is required")
    if CANARY_RECIPIENT != "delivered@resend.dev":
        raise SystemExit("canary recipient lock violated")

    settings = get_settings()
    request = ResendEmailRequest(
        from_address=settings.resend_from,
        to=(CANARY_RECIPIENT,),
        subject=f"Dima Resend Connector Certification {candidate[:12]}",
        text=(
            "Dima connector certification. "
            "No company data, user data, analytical result, or PII."
        ),
    )
    attempt_id = f"resend-connector-certification/{candidate}"

    with ResendEmailConnector(settings=settings) as connector:
        first = connector.send(request=request, attempt_id=attempt_id)
        if first.state != ResendSendState.PROVIDER_ACCEPTED or not first.provider_email_id:
            raise SystemExit(
                f"first POST did not establish provider identity: {first.state.value}"
            )

        second = connector.send(request=request, attempt_id=attempt_id)
        if second.state != ResendSendState.PROVIDER_ACCEPTED or not second.provider_email_id:
            raise SystemExit(
                f"second same-key POST did not resolve provider identity: {second.state.value}"
            )
        if second.provider_email_id != first.provider_email_id:
            raise SystemExit("same-key same-payload provider identity mismatch")

        retrieved = connector.retrieve_email(
            email_id=first.provider_email_id,
            expected_request=request,
        )

    receipt = {
        "candidate": candidate,
        "recipient": CANARY_RECIPIENT,
        "real_recipient_count": 0,
        "logical_send_count": 1,
        "external_post_count": 2,
        "first_provider_email_id": first.provider_email_id,
        "second_provider_email_id": second.provider_email_id,
        "provider_ids_identical": True,
        "retrieve": retrieved.model_dump(mode="json"),
        "payload_fingerprint": first.payload_fingerprint,
        "idempotency_key_fingerprint": first.idempotency_key_fingerprint,
        "credential_disclosed": False,
    }
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(
        json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
