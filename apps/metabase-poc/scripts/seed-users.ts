// Provision the POC organizations (= analytics tenants) and demo users. Idempotent.
//
//   Demo Boyahane (slug boyahane): ayse@boyahane.demo (owner), emre@boyahane.demo (member)
//   Demo Ticaret  (slug tenant2):  mehmet@ticaret.demo (owner)
//
// Org slugs must match the tenant slugs written by dima-metabase/bootstrap/setup.py.
process.env.AUTH_PROVISIONING = "true";

const { auth } = await import("../src/lib/auth");
const { Pool } = await import("pg");
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

const PASSWORD = process.env.SEED_PASSWORD ?? "DimaDemo!2026";

const ORGS = [
  {
    name: "Demo Boyahane",
    slug: "boyahane",
    users: [
      { email: "ayse@boyahane.demo", name: "Ayşe Yılmaz", role: "owner" },
      { email: "emre@boyahane.demo", name: "Emre Demir", role: "member" },
    ],
  },
  {
    name: "Demo Ticaret",
    slug: "tenant2",
    users: [{ email: "mehmet@ticaret.demo", name: "Mehmet Kaya", role: "owner" }],
  },
] as const;

async function userId(email: string, name: string): Promise<string> {
  const found = await pool.query<{ id: string }>('SELECT id FROM "user" WHERE email = $1', [email]);
  if (found.rows[0]) return found.rows[0].id;
  const res = await auth.api.signUpEmail({ body: { email, password: PASSWORD, name } });
  return res.user.id;
}

for (const org of ORGS) {
  const [owner, ...rest] = org.users;
  const ownerId = await userId(owner.email, owner.name);
  let orgId = (await pool.query<{ id: string }>('SELECT id FROM "organization" WHERE slug = $1', [org.slug]))
    .rows[0]?.id;
  if (!orgId) {
    const created = await auth.api.createOrganization({
      body: { name: org.name, slug: org.slug, userId: ownerId },
    });
    orgId = created!.id;
  }
  for (const u of rest) {
    const uid = await userId(u.email, u.name);
    const member = await pool.query('SELECT 1 FROM "member" WHERE "organizationId" = $1 AND "userId" = $2', [
      orgId,
      uid,
    ]);
    if (!member.rowCount) {
      await auth.api.addMember({ body: { userId: uid, organizationId: orgId, role: u.role } });
    }
  }
  console.log(`${org.slug}: ${org.users.map((u) => `${u.email} (${u.role})`).join(", ")}`);
}
console.log(`password for all demo users: ${PASSWORD}`);
await pool.end();
process.exit(0);

export {};
