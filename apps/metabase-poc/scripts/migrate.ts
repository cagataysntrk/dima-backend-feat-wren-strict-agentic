// Create/upgrade the Better Auth tables in DATABASE_URL (dima_auth). Idempotent.
import { getMigrations } from "better-auth/db/migration";
import { auth } from "../src/lib/auth";

const { toBeCreated, toBeAdded, runMigrations } = await getMigrations(auth.options);
await runMigrations();
console.log(
  `auth schema ok — created: ${toBeCreated.map((t) => t.table).join(", ") || "none"}; ` +
    `columns added to: ${toBeAdded.map((t) => t.table).join(", ") || "none"}`,
);
process.exit(0);
