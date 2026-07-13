import Image, { type ImageProps } from "next/image";

import { cn } from "@/utils";

type OptimizedImageProps = Omit<ImageProps, "alt"> & {
  alt: string;
};

/**
 * Wrapper around next/image with production defaults:
 * lazy loading, responsive sizes, AVIF/WebP formats (via next.config).
 */
export function OptimizedImage({
  className,
  alt,
  loading = "lazy",
  quality = 85,
  sizes = "(max-width: 768px) 100vw, 50vw",
  ...props
}: OptimizedImageProps) {
  return (
    <Image
      alt={alt}
      className={cn("h-auto max-w-full", className)}
      loading={loading}
      quality={quality}
      sizes={sizes}
      {...props}
    />
  );
}
