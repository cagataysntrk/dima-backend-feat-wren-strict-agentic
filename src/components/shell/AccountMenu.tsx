"use client";

import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { ChevronsUpDown, LogOut, Monitor, Moon, Sun, Languages } from "lucide-react";
import { useTheme } from "next-themes";
import { logout } from "@/lib/api-client";
import { useMe } from "@/lib/access";
import { setLocale } from "@/i18n/actions";
import { LOCALES, LOCALE_LABELS } from "@/i18n/config";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { SidebarMenuButton } from "@/components/ui/sidebar";

/**
 * Bottom-left account entry (ChatGPT/Claude pattern): avatar + name, opening a
 * menu that collects the low-frequency chrome — tema, dil, çıkış. Keeps the
 * sidebar footer to a single row instead of four loose icon buttons.
 */
export function AccountMenu() {
  const t = useTranslations();
  const router = useRouter();
  const me = useMe();
  const { theme, setTheme } = useTheme();

  const name = me?.email?.split("@")[0] ?? "—";
  const initial = (name[0] ?? "?").toUpperCase();

  async function onLogout() {
    try {
      await logout();
    } finally {
      router.push("/login");
    }
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <SidebarMenuButton size="lg" className="gap-2">
          <Avatar className="size-7 shrink-0 border border-border">
            <AvatarFallback className="rounded-[inherit] bg-brand/10 text-xs text-brand">
              {initial}
            </AvatarFallback>
          </Avatar>
          <span className="min-w-0 flex-1 truncate text-sm">{name}</span>
          <ChevronsUpDown className="size-4 shrink-0 text-muted-foreground" />
        </SidebarMenuButton>
      </DropdownMenuTrigger>

      <DropdownMenuContent side="top" align="start" className="w-56">
        <DropdownMenuLabel className="truncate font-normal text-muted-foreground">
          {me?.email ?? "—"}
        </DropdownMenuLabel>
        <DropdownMenuSeparator />

        <DropdownMenuSub>
          <DropdownMenuSubTrigger>
            <Sun className="size-4" />
            {t("common.theme")}
          </DropdownMenuSubTrigger>
          <DropdownMenuSubContent>
            <DropdownMenuRadioGroup value={theme} onValueChange={setTheme}>
              <DropdownMenuRadioItem value="light">
                <Sun className="size-4" />
                {t("common.themeLight")}
              </DropdownMenuRadioItem>
              <DropdownMenuRadioItem value="dark">
                <Moon className="size-4" />
                {t("common.themeDark")}
              </DropdownMenuRadioItem>
              <DropdownMenuRadioItem value="system">
                <Monitor className="size-4" />
                {t("common.themeSystem")}
              </DropdownMenuRadioItem>
            </DropdownMenuRadioGroup>
          </DropdownMenuSubContent>
        </DropdownMenuSub>

        <DropdownMenuSub>
          <DropdownMenuSubTrigger>
            <Languages className="size-4" />
            {t("common.language")}
          </DropdownMenuSubTrigger>
          <DropdownMenuSubContent>
            {LOCALES.map((l) => (
              <DropdownMenuItem key={l} onSelect={() => void setLocale(l)}>
                {LOCALE_LABELS[l]}
              </DropdownMenuItem>
            ))}
          </DropdownMenuSubContent>
        </DropdownMenuSub>

        <DropdownMenuSeparator />
        <DropdownMenuItem onSelect={onLogout} variant="destructive">
          <LogOut className="size-4" />
          {t("common.logout")}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
