import { useTranslations } from "next-intl";
import { Lock } from "lucide-react";

export function NoAccess() {
  const t = useTranslations("noAccess");
  return (
    <div className="surface mx-auto max-w-md space-y-2 p-6 text-center">
      <Lock className="mx-auto size-5 text-muted-foreground" aria-hidden />
      <h1 className="font-medium">{t("title")}</h1>
      <p className="text-sm text-muted-foreground">
        {t("body")}
      </p>
    </div>
  );
}
