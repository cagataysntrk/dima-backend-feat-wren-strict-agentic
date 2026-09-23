import "server-only";
import { createCipheriv, createDecipheriv, createHash, randomBytes } from "node:crypto";
import { GatewayError } from "@/server/metabase/errors";
import type { NativeEngineContext } from "./types";

const VERSION = 1;
const IV_BYTES = 12;
const TAG_BYTES = 16;
const MAX_TOKEN_BYTES = 512_000;

function key(): Buffer {
  const secret = process.env.BETTER_AUTH_SECRET;
  if (!secret || secret === "change-me") {
    throw new Error("BETTER_AUTH_SECRET must be configured before native chat can persist engine context");
  }
  return createHash("sha256").update(`dima-native-engine-context:v1:${secret}`).digest();
}

export function sealEngineContext(value: NativeEngineContext): string {
  const iv = randomBytes(IV_BYTES);
  const cipher = createCipheriv("aes-256-gcm", key(), iv);
  const plaintext = Buffer.from(JSON.stringify(value), "utf8");
  const encrypted = Buffer.concat([cipher.update(plaintext), cipher.final()]);
  const tag = cipher.getAuthTag();
  return Buffer.concat([Buffer.from([VERSION]), iv, tag, encrypted]).toString("base64url");
}

export function openEngineContext(
  token: string | null | undefined,
  expected: { tenantSlug: string; productConversationId: string },
): NativeEngineContext | null {
  if (!token) return null;

  let packed: Buffer;
  try {
    packed = Buffer.from(token, "base64url");
    if (packed.toString("base64url") !== token) {
      throw new Error("non-canonical context token");
    }
  } catch {
    throw new GatewayError(400, "Sohbet bağlamı geçersiz.");
  }
  if (packed.length > MAX_TOKEN_BYTES || packed.length < 1 + IV_BYTES + TAG_BYTES) {
    throw new GatewayError(400, "Sohbet bağlamı geçersiz.");
  }
  if (packed[0] !== VERSION) throw new GatewayError(400, "Sohbet bağlamı sürümü desteklenmiyor.");

  try {
    const iv = packed.subarray(1, 1 + IV_BYTES);
    const tag = packed.subarray(1 + IV_BYTES, 1 + IV_BYTES + TAG_BYTES);
    const encrypted = packed.subarray(1 + IV_BYTES + TAG_BYTES);
    const decipher = createDecipheriv("aes-256-gcm", key(), iv);
    decipher.setAuthTag(tag);
    const decoded = Buffer.concat([decipher.update(encrypted), decipher.final()]).toString("utf8");
    const value = JSON.parse(decoded) as NativeEngineContext;
    if (
      value.version !== 1 ||
      value.tenantSlug !== expected.tenantSlug ||
      value.productConversationId !== expected.productConversationId ||
      !Array.isArray(value.history) ||
      !value.state ||
      typeof value.state !== "object"
    ) {
      throw new Error("context binding mismatch");
    }
    return value;
  } catch {
    throw new GatewayError(400, "Sohbet bağlamı geçersiz.");
  }
}
