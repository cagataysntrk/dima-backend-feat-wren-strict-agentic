import { Lock } from "lucide-react";

export function NoAccess() {
  return (
    <div className="mx-auto max-w-md space-y-2 rounded-xl border bg-card p-6 text-center">
      <Lock className="mx-auto size-5 text-muted-foreground" aria-hidden />
      <h1 className="font-medium">Bu sayfa için yetkiniz yok</h1>
      <p className="text-sm text-muted-foreground">
        SQL çalıştırma ve veri yükleme yalnızca şirket yöneticilerine açıktır.
      </p>
    </div>
  );
}
