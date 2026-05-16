"use client";

import Image from "next/image";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

export function BrandLogo({
  variant = "full",
  className,
  priority,
}: {
  variant?: "full" | "icon";
  className?: string;
  priority?: boolean;
}) {
  const [isLight, setIsLight] = useState(false);

  useEffect(() => {
    const root = document.documentElement;
    const read = () =>
      setIsLight(root.getAttribute("data-theme") === "light");
    read();
    const observer = new MutationObserver(read);
    observer.observe(root, { attributes: true, attributeFilter: ["data-theme"] });
    return () => observer.disconnect();
  }, []);

  // Always use the dark (white-on-transparent) PNGs.
  // In light mode we invert them: white logo → black logo, transparent stays transparent.
  const src = variant === "full" ? "/brand/logo-full.png" : "/brand/logo-icon.png";
  const width  = variant === "full" ? 280 : 64;
  const height = variant === "full" ? 96  : 64;

  return (
    <Image
      src={src}
      alt="AYANAMI AGENT"
      width={width}
      height={height}
      priority={priority}
      className={cn(
        "object-contain transition-[filter] duration-300",
        isLight ? "invert" : "",
        className
      )}
    />
  );
}
