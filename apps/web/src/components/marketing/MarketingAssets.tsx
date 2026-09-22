import Image from "next/image";
import { cn } from "@dima/ui/utils";

export type MarketingAssetKey =
  | "homeHero"
  | "homeQuality"
  | "homeFloor"
  | "homeTrust"
  | "homeConnections"
  | "homeCta"
  | "productHero"
  | "howHero"
  | "solutionsHero"
  | "textileHero"
  | "securityHero"
  | "integrationsHero"
  | "aboutHero"
  | "contactHero";

const assets = {
  homeHero: {
    src: "/marketing/dyehouse-operator-hero.avif",
    width: 1672,
    height: 941,
  },
  homeQuality: {
    src: "/marketing/fabric-quality-inspection.avif",
    width: 1448,
    height: 1086,
  },
  homeFloor: {
    src: "/marketing/dyehouse-machine-floor.avif",
    width: 1672,
    height: 941,
  },
  homeTrust: {
    src: "/marketing/operations-review.avif",
    width: 1727,
    height: 911,
  },
  homeConnections: {
    src: "/marketing/decision-field.avif",
    width: 1728,
    height: 920,
  },
  homeCta: {
    src: "/marketing/evidence-archive.avif",
    width: 1488,
    height: 1116,
  },
  productHero: {
    src: "/marketing/product-analyst-hero.avif",
    width: 1568,
    height: 1003,
  },
  howHero: {
    src: "/marketing/workflow-sequence-hero.avif",
    width: 1536,
    height: 1024,
  },
  solutionsHero: {
    src: "/marketing/solutions-operations-hero.avif",
    width: 1672,
    height: 941,
  },
  textileHero: {
    src: "/marketing/textile-inspection-hero.avif",
    width: 1748,
    height: 900,
  },
  securityHero: {
    src: "/marketing/security-access-hero.avif",
    width: 1586,
    height: 992,
  },
  integrationsHero: {
    src: "/marketing/integrations-wiring-hero.avif",
    width: 1672,
    height: 941,
  },
  aboutHero: {
    src: "/marketing/about-studio-hero.avif",
    width: 1586,
    height: 992,
  },
  contactHero: {
    src: "/marketing/contact-conversation-hero.avif",
    width: 1536,
    height: 1024,
  },
} satisfies Record<
  MarketingAssetKey,
  { src: string; width: number; height: number }
>;

export function MarketingEditorialImage({
  asset,
  alt = "",
  className,
  priority = false,
  sizes = "(min-width: 1024px) 50vw, 100vw",
}: {
  asset: MarketingAssetKey;
  alt?: string;
  className?: string;
  priority?: boolean;
  sizes?: string;
}) {
  const image = assets[asset];
  return (
    <Image
      alt={alt}
      className={cn("size-full object-cover", className)}
      height={image.height}
      priority={priority}
      sizes={sizes}
      src={image.src}
      width={image.width}
    />
  );
}
