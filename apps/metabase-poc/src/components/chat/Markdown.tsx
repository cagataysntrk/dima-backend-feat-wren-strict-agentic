"use client";

import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import { cn } from "@dima/ui/utils";

// Chat answers are model output rendered as Markdown (GFM: bold, lists,
// tables). react-markdown never renders raw HTML; images are dropped and links
// are limited to http(s) and open in a new tab without referrer/opener.

const components: Components = {
  p: ({ children }) => <p className="leading-relaxed">{children}</p>,
  strong: ({ children }) => <strong className="font-semibold text-foreground">{children}</strong>,
  em: ({ children }) => <em className="text-foreground/90">{children}</em>,
  h1: ({ children }) => <h3 className="text-base font-semibold tracking-tight">{children}</h3>,
  h2: ({ children }) => <h3 className="text-base font-semibold tracking-tight">{children}</h3>,
  h3: ({ children }) => <h3 className="text-[15px] font-semibold tracking-tight">{children}</h3>,
  h4: ({ children }) => <h4 className="text-sm font-semibold">{children}</h4>,
  ul: ({ children }) => <ul className="ml-4 list-disc space-y-1 marker:text-brand/70">{children}</ul>,
  ol: ({ children }) => <ol className="ml-4 list-decimal space-y-1 marker:text-muted-foreground">{children}</ol>,
  li: ({ children }) => <li className="pl-1 leading-relaxed">{children}</li>,
  a: ({ href, children }) =>
    href && /^https?:\/\//i.test(href) ? (
      <a href={href} target="_blank" rel="noopener noreferrer" className="text-brand underline-offset-4 hover:underline">
        {children}
      </a>
    ) : (
      <span>{children}</span>
    ),
  code: ({ children }) => (
    <code className="rounded-md bg-muted px-1.5 py-0.5 font-mono text-[0.85em]">{children}</code>
  ),
  pre: ({ children }) => (
    <pre className="surface-inset overflow-x-auto p-3 font-mono text-xs leading-relaxed">{children}</pre>
  ),
  blockquote: ({ children }) => (
    <blockquote className="border-l-2 border-brand/40 pl-3 text-muted-foreground">{children}</blockquote>
  ),
  hr: () => <hr className="border-[var(--surface-edge)]" />,
  table: ({ children }) => (
    <div className="surface-inset overflow-x-auto">
      <table className="w-full border-collapse text-sm tabular-nums">{children}</table>
    </div>
  ),
  thead: ({ children }) => <thead className="text-xs text-muted-foreground">{children}</thead>,
  th: ({ children, style }) => (
    <th style={style} className="border-b border-[var(--surface-edge)] px-3 py-2 text-left font-medium">
      {children}
    </th>
  ),
  td: ({ children, style }) => (
    <td style={style} className="border-b border-[var(--surface-edge)] px-3 py-2 last:border-0">
      {children}
    </td>
  ),
  tr: ({ children }) => <tr className="[&:last-child>td]:border-b-0">{children}</tr>,
  img: () => null,
};

export function Markdown({ children, className }: { children: string; className?: string }) {
  return (
    <div className={cn("space-y-3 text-sm", className)}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components} skipHtml>
        {children}
      </ReactMarkdown>
    </div>
  );
}
