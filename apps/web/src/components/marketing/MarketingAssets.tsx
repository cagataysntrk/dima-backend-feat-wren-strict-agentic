import Image from "next/image";
import { cn } from "@/lib/utils";

export type MarketingAssetKey =
  | "hero"
  | "quality"
  | "floor"
  | "review"
  | "decisions"
  | "archive";

const assets = {
  hero: {
    src: "/marketing/dyehouse-operator-hero.avif",
    width: 1672,
    height: 941,
  },
  quality: {
    src: "/marketing/fabric-quality-inspection.avif",
    width: 1448,
    height: 1086,
  },
  floor: {
    src: "/marketing/dyehouse-machine-floor.avif",
    width: 1672,
    height: 941,
  },
  review: {
    src: "/marketing/operations-review.avif",
    width: 1727,
    height: 911,
  },
  decisions: {
    src: "/marketing/decision-field.avif",
    width: 1728,
    height: 920,
  },
  archive: {
    src: "/marketing/evidence-archive.avif",
    width: 1488,
    height: 1116,
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
