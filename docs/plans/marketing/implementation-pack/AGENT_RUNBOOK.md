# Agent Runbook

Bu runbook, master prompt ve stage dosyalarıyla çalışan AI coding agent için ortak yürütme protokolüdür.

## 1. Oturum başında

Agent önce:

```bash
pwd
git status --short
git branch --show-current
git log -5 --oneline
cat package.json
```

Ardından:
- mevcut uncommitted değişiklikleri listeler,
- hiçbir değişikliği silmez veya overwrite etmez,
- hedef stage dışındaki dosyalara dokunmaz,
- ilgili repo docs/standards/CLAUDE/AGENTS dosyalarını okur.

## 2. Referans inceleme

Dima repo içi source of truth:
- `README.md`
- `src/app`
- `src/proxy.ts`
- `src/app/layout.tsx`
- `src/app/globals.css`
- `src/lib/providers.tsx`
- `src/lib/motion.ts`
- `messages/*.json`
- `e2e/`
- `saka-standards` ve proje yönergeleri

UpcyMan salt-okunur:
`/Users/enesteve/Desktop/Coding/Upcy/upcyman/upcyman`

Agent:
- yalnızca inceleyebilir,
- değiştiremez,
- import/symlink/dependency yapamaz,
- Dima'ya uygun yeniden uygulama yapar.

## 3. Stage başlamadan önce verilecek kısa rapor

```markdown
## Stage Preflight
- Current branch:
- Working tree:
- Relevant current files:
- Constraints discovered:
- Planned files to change:
- Risks:
```

Kullanıcı açıkça “devam et” beklenmesini istemediyse agent doğrudan implement edebilir; ancak bu preflight'i kendi çalışma logunda tutmalıdır.

## 4. Implementation rules

- Strict TypeScript, `any` yok.
- Server Component default.
- Client boundary minimum.
- Existing business logic untouched.
- No broad formatting churn.
- No dependency without explanation.
- No fake content.
- No secrets/PII.
- Accessible semantics.
- Responsive by construction.
- Tests after meaningful checkpoints.
- One stage, one scope.

## 5. Validation order

1. Targeted type/lint.
2. Full lint.
3. Production build.
4. Stage-specific test.
5. Auth/product smoke if routing/providers touched.
6. Visual responsive check.
7. Git diff review.

## 6. Hata yaklaşımı

Bir test mevcut baseline'da zaten fail ediyorsa:
- exact command,
- exact failure,
- neden stage kaynaklı olmadığını,
- stage'in yeni failure ekleyip eklemediğini
belgele.

Testi susturmak, skip etmek veya config'i gevşetmek çözüm değildir.

## 7. Stage sonu raporu

```markdown
# Stage Completion Report

## Summary
## Files changed
## Key implementation decisions
## Validation performed
- `command` — PASS/FAIL

## Accessibility checks
## Performance considerations
## Security/auth regression checks
## Known limitations
## Deferred work
## Recommended next stage
```

## 8. Git davranışı

- Kullanıcı istemedikçe commit yapma.
- Kullanıcı istemedikçe push yapma.
- Branch değiştirme veya reset yapma.
- `git clean`, `git reset --hard`, force push yok.
- UpcyMan repo'sunda hiçbir git komutu değişiklik üretmemeli.
