import { betterAuth } from "better-auth";
import { nextCookies } from "better-auth/next-js";
import { organization } from "better-auth/plugins";
import { Pool } from "pg";

// Better Auth — email+password login; the organization plugin models tenants.
// An organization's slug IS the analytics tenant slug (see server/metabase/tenants.ts).
// Roles: owner | admin | member. Owner/admin may run SQL and upload data.
//
// Public sign-up is off: users are provisioned (scripts/seed-users.ts, later an
// admin flow). The seed script flips AUTH_PROVISIONING=true for its own process.
const provisioning = process.env.AUTH_PROVISIONING === "true";

const pool = new Pool({ connectionString: process.env.DATABASE_URL, max: 5 });

export const auth = betterAuth({
  appName: "dima",
  database: pool,
  emailAndPassword: {
    enabled: true,
    disableSignUp: !provisioning,
    minPasswordLength: 10,
  },
  session: {
    expiresIn: 60 * 60 * 8, // 8h working session
    updateAge: 60 * 60,
  },
  databaseHooks: {
    session: {
      create: {
        // Land every new session in the user's first organization, so the
        // gateway always has a tenant context right after login.
        before: async (session) => {
          const { rows } = await pool.query<{ organizationId: string }>(
            'SELECT "organizationId" FROM "member" WHERE "userId" = $1 ORDER BY "createdAt" LIMIT 1',
            [session.userId],
          );
          return { data: { ...session, activeOrganizationId: rows[0]?.organizationId ?? null } };
        },
      },
    },
  },
  plugins: [
    organization({
      allowUserToCreateOrganization: async () => provisioning,
    }),
    nextCookies(),
  ],
});

export type Session = typeof auth.$Infer.Session;
