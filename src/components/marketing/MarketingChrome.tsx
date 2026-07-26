"use client";

import Link from "next/link";
import { Menu } from "lucide-react";
import { BrandMark } from "@/components/BrandMark";
import { LocaleSwitcher } from "@/components/shell/LocaleSwitcher";
import { ThemeToggle } from "@/components/shell/ThemeToggle";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import type { MarketingContent } from "@/content/marketing";

const navigation = [
  { key: "product", href: "/product" },
  { key: "how", href: "/how-it-works" },
  { key: "solutions", href: "/solutions" },
  { key: "security", href: "/security" },
  { key: "integrations", href: "/integrations" },
] as const;

export function MarketingHeader({ content }: { content: MarketingContent }) {
  return (
    <header className="sticky top-0 z-40 border-b bg-background/90 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center gap-5 px-5 sm:px-8">
        <Link href="/" aria-label={content.locale === "tr" ? "dima ana sayfa" : "dima home"} className="rounded-sm focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-ring">
          <BrandMark size="md" />
        </Link>
        <nav aria-label={content.locale === "tr" ? "Ana navigasyon" : "Main navigation"} className="ml-auto hidden items-center gap-1 lg:flex">
          {navigation.map((item) => (
            <Link
              key={item.key}
              href={item.href}
              className="rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-foreground focus-visible:outline-2 focus-visible:outline-ring"
            >
              {content.nav[item.key]}
            </Link>
          ))}
        </nav>
        <div className="ml-auto flex items-center gap-1 lg:ml-3">
          <LocaleSwitcher />
          <ThemeToggle />
          <Button asChild variant="ghost" className="hidden sm:inline-flex">
            <Link href="/login">{content.nav.login}</Link>
          </Button>
          <Button asChild variant="brand" className="hidden sm:inline-flex">
            <Link href="/contact">{content.nav.demo}</Link>
          </Button>
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="outline" size="icon" className="lg:hidden" aria-label={content.nav.menu}>
                <Menu />
              </Button>
            </SheetTrigger>
            <SheetContent>
              <SheetHeader className="border-b">
                <SheetTitle><BrandMark size="md" /></SheetTitle>
                <SheetDescription>{content.footer.statement}</SheetDescription>
              </SheetHeader>
              <nav aria-label={content.locale === "tr" ? "Mobil navigasyon" : "Mobile navigation"} className="grid gap-1 px-4">
                {navigation.map((item) => (
                  <SheetClose asChild key={item.key}>
                    <Link href={item.href} className="rounded-md px-3 py-3 text-base hover:bg-accent focus-visible:outline-2 focus-visible:outline-ring">
                      {content.nav[item.key]}
                    </Link>
                  </SheetClose>
                ))}
              </nav>
              <div className="mt-auto grid gap-2 border-t p-4">
                <SheetClose asChild><Button asChild variant="outline"><Link href="/login">{content.nav.login}</Link></Button></SheetClose>
                <SheetClose asChild><Button asChild variant="brand"><Link href="/contact">{content.nav.demo}</Link></Button></SheetClose>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  );
}

export function MarketingFooter({ content }: { content: MarketingContent }) {
  const year = new Date().getFullYear();
  return (
    <footer className="border-t bg-muted/35">
      <div className="mx-auto grid max-w-7xl gap-10 px-5 py-14 sm:px-8 md:grid-cols-[1.6fr_1fr_1fr_1fr]">
        <div>
          <BrandMark size="md" />
          <p className="mt-4 max-w-sm text-sm leading-6 text-muted-foreground">{content.footer.statement}</p>
        </div>
        <FooterGroup title={content.footer.product} links={[
          [content.nav.product, "/product"],
          [content.nav.how, "/how-it-works"],
          [content.nav.integrations, "/integrations"],
        ]} />
        <FooterGroup title={content.footer.company} links={[
          [content.footer.about, "/about"],
          [content.footer.contact, "/contact"],
          [content.nav.security, "/security"],
        ]} />
        <FooterGroup title={content.footer.legal} links={[
          [content.footer.privacy, "/privacy"],
          [content.footer.terms, "/terms"],
        ]} />
      </div>
      <div className="border-t px-5 py-5 text-center text-xs text-muted-foreground">
        © {year} UpcyTech Teknoloji A.Ş. {content.footer.rights}
      </div>
    </footer>
  );
}

function FooterGroup({ title, links }: { title: string; links: [string, string][] }) {
  return (
    <div>
      <h2 className="font-mono text-xs uppercase tracking-[0.18em]">{title}</h2>
      <ul className="mt-4 space-y-3 text-sm text-muted-foreground">
        {links.map(([label, href]) => <li key={href}><Link className="hover:text-foreground hover:underline" href={href}>{label}</Link></li>)}
      </ul>
    </div>
  );
}
