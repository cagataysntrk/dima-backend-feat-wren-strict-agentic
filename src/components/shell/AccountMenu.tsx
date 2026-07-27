"use client";

import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import Link from "next/link";
import {
  ChevronsUpDown,
  HelpCircle,
  Keyboard,
  LogOut,
  Monitor,
  Moon,
  RotateCcw,
  Settings,
  Sun,
  Languages,
} from "lucide-react";
import { useTheme } from "next-themes";
import { logout } from "@/lib/api-client";
import { useConversations } from "@/stores/conversations";
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
  DropdownMenuShortcut,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Kbd, KbdGroup } from "@/components/ui/kbd";
import { Skeleton } from "@/components/ui/skeleton";
import { SidebarMenuButton } from "@/components/ui/sidebar";
import { ConnectionBadge } from "@/components/ConnectionBadge";
import { resetOnboarding, useOnboardingDismissed } from "./Onboarding";

/**
 * Bottom-left account entry (ChatGPT/Claude pattern): avatar + name, opening a
 * menu that collects the low-frequency chrome — tema, dil, çıkış. Keeps the
 * sidebar footer to a single row instead of four loose icon buttons.
 */
export function AccountMenu({
  onOpenHelp,
  onOpenShortcuts,
}: {
  onOpenHelp: () => void;
  onOpenShortcuts: () => void;
}) {
  const t = useTranslations();
  const router = useRouter();
  const me = useMe();
  const { theme, setTheme } = useTheme();
  const onboardingDismissed = useOnboardingDismissed();

  // /auth/me henüz gelmediyse "—" yazmak yerine iskelet göster (yükleniyor ≠ boş isim).
  const name = me?.email?.split("@")[0] ?? null;
  const initial = name ? name[0]!.toUpperCase() : "";

  async function onLogout() {
    try {
      await logout();
    } finally {
      // ÇIKIŞTA KONUŞMA DURUMUNU TEMİZLE (güvenlik/izolasyon, canlı 2026-07-25): geçmiş global
      // Zustand store'da; temizlenmezse LOGOUT sonrası BAŞKA kullanıcı önceki kullanıcının tüm
      // konuşma/rapor zincirini görürdü (çapraz-kullanıcı sızıntı).
      useConversations.getState().reset();
      router.push("/login");
    }
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <SidebarMenuButton size="lg" className="gap-2">
          {/* veri kaynağı durumu avatarın üstünde küçük bir nokta (presence deseni) —
              satırda ayrı bir ikon olarak durmasın diye */}
          <span className="relative shrink-0">
            <Avatar className="size-7 border border-border">
              <AvatarFallback className="rounded-[inherit] bg-brand/10 text-xs font-medium text-brand">
                {initial}
              </AvatarFallback>
            </Avatar>
            <ConnectionBadge className="absolute -right-0.5 -bottom-0.5" />
          </span>
          {name ? (
            <span className="min-w-0 flex-1 truncate text-sm">{name}</span>
          ) : (
            <Skeleton className="h-3.5 min-w-0 flex-1" />
          )}
          <ChevronsUpDown className="size-4 shrink-0 text-muted-foreground" />
        </SidebarMenuButton>
      </DropdownMenuTrigger>

      <DropdownMenuContent side="top" align="start" className="w-56">
        <DropdownMenuLabel className="truncate font-normal text-muted-foreground">
          {me?.email ?? "…"}
        </DropdownMenuLabel>
        <DropdownMenuSeparator />

        <DropdownMenuItem asChild>
          <Link href="/settings">
            <Settings className="size-4" />
            {t("common.settings")}
            <DropdownMenuShortcut>
              <KbdGroup>
                <Kbd>⌘</Kbd>
                <Kbd>,</Kbd>
              </KbdGroup>
            </DropdownMenuShortcut>
          </Link>
        </DropdownMenuItem>

        <DropdownMenuItem onSelect={onOpenHelp}>
          <HelpCircle className="size-4" />
          {t("common.help")}
        </DropdownMenuItem>

        <DropdownMenuItem onSelect={onOpenShortcuts}>
          <Keyboard className="size-4" />
          Klavye kısayolları
          <DropdownMenuShortcut>
            <KbdGroup>
              <Kbd>⌘</Kbd>
              <Kbd>/</Kbd>
            </KbdGroup>
          </DropdownMenuShortcut>
        </DropdownMenuItem>

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

        {/* Gizlenen/biten turu geri getir — aksi halde "Gizle" tek yönlü kapı olurdu */}
        {onboardingDismissed && (
          <>
            <DropdownMenuSeparator />
            <DropdownMenuItem onSelect={resetOnboarding}>
              <RotateCcw className="size-4" />
              Başlangıç turunu göster
            </DropdownMenuItem>
          </>
        )}

        <DropdownMenuSeparator />
        <DropdownMenuItem onSelect={onLogout} variant="destructive">
          <LogOut className="size-4" />
          {t("common.logout")}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
