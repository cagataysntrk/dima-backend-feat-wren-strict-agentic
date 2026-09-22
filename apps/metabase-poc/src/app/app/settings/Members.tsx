"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { Copy, Trash2, UserPlus } from "lucide-react";
import { toast } from "sonner";
import { gateway, type Member } from "@/lib/gateway";
import { Button } from "@dima/ui/primitives/button";
import { Input } from "@dima/ui/primitives/input";
import { Label } from "@dima/ui/primitives/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@dima/ui/primitives/select";
import { Skeleton } from "@dima/ui/primitives/skeleton";

/** Message keys per role — the wording itself lives in messages/*.json. */
const ROLE_KEY: Record<Member["role"], "roleOwner" | "roleAdmin" | "roleMember"> = {
  owner: "roleOwner",
  admin: "roleAdmin",
  member: "roleMember",
};

export function Members() {
  const queryClient = useQueryClient();
  const t = useTranslations("settings.members");
  const [adding, setAdding] = useState(false);
  // Shown once, right after creating a user: there is no mailer to send it.
  const [tempPassword, setTempPassword] = useState<{ email: string; password: string } | null>(null);
  const data = useQuery({ queryKey: ["members"], queryFn: gateway.members });
  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["members"] });

  const setRole = useMutation({
    mutationFn: ({ id, role }: { id: string; role: "admin" | "member" }) => gateway.setMemberRole(id, role),
    onSuccess: () => {
      toast.success(t("roleUpdated"));
      void invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });
  const remove = useMutation({
    mutationFn: (id: string) => gateway.removeMember(id),
    onSuccess: () => {
      toast.success(t("removed"));
      void invalidate();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  if (data.isPending) {
    return (
      <div className="space-y-2">
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-12 w-full" />
      </div>
    );
  }
  if (data.isError) {
    return (
      <p role="alert" className="text-sm text-destructive">
        {data.error.message}
      </p>
    );
  }

  const { members, myRole, myMemberId } = data.data;
  const isOwner = myRole === "owner";

  return (
    <div className="space-y-4">
      <ul className="divide-y divide-[var(--surface-edge)]">
        {members.map((m) => (
          <li key={m.id} className="flex flex-wrap items-center gap-3 py-2.5">
            <span className="grid size-8 shrink-0 place-items-center rounded-full bg-muted text-xs font-semibold">
              {m.name.slice(0, 1).toLocaleUpperCase("tr-TR")}
            </span>
            <span className="min-w-0 flex-1">
              <span className="block truncate text-sm font-medium">
                {m.name}
                {m.id === myMemberId && <span className="ml-1.5 text-xs text-muted-foreground">{t("you")}</span>}
              </span>
              <span className="block truncate text-xs text-muted-foreground">{m.email}</span>
            </span>
            {isOwner && m.role !== "owner" && m.id !== myMemberId ? (
              <Select
                value={m.role}
                onValueChange={(role) => setRole.mutate({ id: m.id, role: role as "admin" | "member" })}
              >
                <SelectTrigger size="sm" className="w-36" aria-label={t("roleOf", { name: m.name })}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="admin">{t("roleAdmin")}</SelectItem>
                  <SelectItem value="member">{t("roleMember")}</SelectItem>
                </SelectContent>
              </Select>
            ) : (
              <span className="text-xs text-muted-foreground">{t(ROLE_KEY[m.role])}</span>
            )}
            {isOwner && m.role !== "owner" && m.id !== myMemberId && (
              <Button
                variant="ghost"
                size="icon-sm"
                aria-label={t("removeMember", { name: m.name })}
                onClick={() => remove.mutate(m.id)}
                disabled={remove.isPending}
                className="text-muted-foreground hover:text-destructive"
              >
                <Trash2 className="size-4" aria-hidden />
              </Button>
            )}
          </li>
        ))}
      </ul>

      <p className="text-xs text-muted-foreground">
        {t("roleAdmin")}: {t("hintAdmin")} · {t("roleMember")}: {t("hintMember")}
      </p>

      {tempPassword && (
        <div className="surface-inset space-y-2 p-3">
          <p className="text-sm font-medium">{t("tempPasswordFor", { email: tempPassword.email })}</p>
          <div className="flex items-center gap-2">
            <code className="min-w-0 flex-1 truncate rounded-md bg-muted/60 px-2 py-1 font-mono text-sm">
              {tempPassword.password}
            </code>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                void navigator.clipboard?.writeText(tempPassword.password);
                toast.success(t("copied"));
              }}
            >
              <Copy className="size-3.5" aria-hidden />
              {t("copy")}
            </Button>
          </div>
          <p className="text-xs text-muted-foreground">
            {t("tempPasswordNote")}
          </p>
        </div>
      )}

      {isOwner &&
        (adding ? (
          <AddMemberForm
            onDone={(result) => {
              setAdding(false);
              if (result) setTempPassword(result);
              void invalidate();
            }}
          />
        ) : (
          <Button variant="outline" size="sm" onClick={() => setAdding(true)}>
            <UserPlus className="size-4" aria-hidden />
            {t("add")}
          </Button>
        ))}
    </div>
  );
}

function AddMemberForm({ onDone }: { onDone: (temp: { email: string; password: string } | null) => void }) {
  const t = useTranslations("settings.members");
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [role, setRole] = useState<"admin" | "member">("member");

  const add = useMutation({
    mutationFn: () => gateway.addMember({ email: email.trim(), name: name.trim(), role }),
    onSuccess: ({ password }) => {
      toast.success(t("added"));
      onDone(password ? { email: email.trim(), password } : null);
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <form
      onSubmit={(ev) => {
        ev.preventDefault();
        add.mutate();
      }}
      className="surface-inset space-y-3 p-3"
    >
      <div className="grid gap-3 sm:grid-cols-2">
        <div className="space-y-1.5">
          <Label htmlFor="m-name" className="text-xs">
            {t("fullName")}
          </Label>
          <Input id="m-name" value={name} onChange={(e) => setName(e.target.value)} className="h-9" required />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="m-email" className="text-xs">
            {t("email")}
          </Label>
          <Input
            id="m-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="h-9"
            required
          />
        </div>
      </div>
      <div className="flex flex-wrap items-end gap-3">
        <div className="space-y-1.5">
          <Label htmlFor="m-role" className="text-xs">
            {t("role")}
          </Label>
          <Select value={role} onValueChange={(v) => setRole(v as "admin" | "member")}>
            <SelectTrigger id="m-role" size="sm" className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="member">{t("roleMember")}</SelectItem>
              <SelectItem value="admin">{t("roleAdmin")}</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <Button type="submit" variant="brand" size="sm" disabled={add.isPending}>
          {add.isPending ? t("adding") : t("addSubmit")}
        </Button>
        <Button type="button" variant="ghost" size="sm" onClick={() => onDone(null)}>
          {t("cancel")}
        </Button>
      </div>
      <p className="text-xs text-muted-foreground">
        {t("addNote")}
      </p>
    </form>
  );
}
