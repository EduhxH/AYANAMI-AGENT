"use client";

import { motion, type Variants } from "framer-motion";
import { cn } from "@/lib/utils";

const variants: Record<string, Variants> = {
  up: {
    hidden: { opacity: 0, y: 44 },
    visible: { opacity: 1, y: 0 },
  },
  left: {
    hidden: { opacity: 0, x: -52 },
    visible: { opacity: 1, x: 0 },
  },
  right: {
    hidden: { opacity: 0, x: 52 },
    visible: { opacity: 1, x: 0 },
  },
  scale: {
    hidden: { opacity: 0, scale: 0.9, y: 28, filter: "blur(4px)" },
    visible: { opacity: 1, scale: 1, y: 0, filter: "blur(0px)" },
  },
};

interface RevealProps {
  children: React.ReactNode;
  className?: string;
  variant?: keyof typeof variants;
  delay?: number;
  once?: boolean;
}

export function Reveal({
  children,
  className,
  variant = "up",
  delay = 0,
  once = true,
}: RevealProps) {
  return (
    <motion.div
      className={cn(className)}
      initial="hidden"
      whileInView="visible"
      viewport={{ once, amount: 0.12 }}
      transition={{
        duration: 0.85,
        delay,
        ease: [0.16, 1, 0.3, 1],
      }}
      variants={variants[variant]}
    >
      {children}
    </motion.div>
  );
}

export function PageCurtain() {
  return (
    <motion.div
      className="pointer-events-none fixed inset-0 z-[99999] origin-top bg-black"
      initial={{ scaleY: 1, opacity: 1 }}
      animate={{ scaleY: 0, opacity: 0 }}
      transition={{ duration: 1, ease: [0.76, 0, 0.24, 1], delay: 0.1 }}
    />
  );
}
