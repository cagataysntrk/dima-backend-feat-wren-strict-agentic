"use client";

import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import { useTranslations } from "next-intl";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

/** Password field with a show/hide toggle and a Caps-Lock warning. */
export function PasswordInput({
  id,
  value,
  onChange,
  autoComplete = "current-password",
  className,
  ...rest
}: Omit<React.ComponentProps<typeof Input>, "type" | "value" | "onChange"> & {
  id: string;
  value: string;
  onChange: (v: string) => void;
}) {
  const t = useTranslations("auth");
  const [show, setShow] = useState(false);
  const [caps, setCaps] = useState(false);

  return (
    <div className="space-y-1">
      <div className="relative">
        <Input
          id={id}
          type={show ? "text" : "password"}
          autoComplete={autoComplete}
          value={value}
          suppressHydrationWarning
          onChange={(e) => onChange(e.target.value)}
          onKeyUp={(e) => setCaps(e.getModifierState?.("CapsLock") ?? false)}
          className={cn("pr-10", className)}
          {...rest}
        />
        <button
          type="button"
          onClick={() => setShow((s) => !s)}
          aria-label={show ? t("hidePassword") : t("showPassword")}
          className="absolute top-1/2 right-2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground"
        >
          {show ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
        </button>
      </div>
      {caps && (
        <p className="text-[11px] text-amber-600 dark:text-amber-400" aria-live="polite">
          {t("capsLock")}
        </p>
      )}
    </div>
  );
}
