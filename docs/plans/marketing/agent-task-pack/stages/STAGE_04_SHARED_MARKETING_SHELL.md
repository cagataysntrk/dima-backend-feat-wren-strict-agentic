# Stage 04 — Shared Marketing Shell

## Objective

Implement consistent public navigation, mobile behavior, footer, and page chrome before building individual page narratives.

## Tasks

1. Create the shared marketing layout using the route boundary from Stage 01.
2. Navigation:
   - Dima wordmark;
   - Product;
   - How it works;
   - Solutions;
   - Security;
   - Integrations;
   - locale control where supported;
   - login;
   - primary demo CTA.
3. Implement a mobile menu with:
   - visible trigger label;
   - focus management/focus trap;
   - Escape close;
   - click-away close;
   - route-change close;
   - scroll-lock without layout shift;
   - 44px practical controls.
4. Add active-link/current-location treatment that works for nested solutions routes.
5. Add skip link, semantic header, nav, main, and footer.
6. Build footer groups from the approved route list. Do not add empty /pricing, /blog, /docs, or /case-studies links.
7. Decide whether a sticky header is necessary. If sticky, ensure focus and anchor targets are not obscured.
8. Add a small, honest status/announcement strip only if approved content exists; otherwise omit it.

## Acceptance criteria

- All launch routes share the same shell and nav order.
- Keyboard users can enter, operate, and leave the mobile menu.
- Locale and auth links preserve the correct route semantics.
- Footer does not advertise unavailable pages.
- Shell works on 320px, 375px, 768px, 1024px, and 1440px.
- Light/dark modes keep contrast and active states.

## Verification

Test keyboard-only navigation, Escape, resize while menu is open, deep links, and viewport screenshots. Run route smoke and UI quality checks.

