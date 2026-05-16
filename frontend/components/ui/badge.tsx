import { cn } from "@/lib/utils";

export function Badge({
  className,
  variant = "default",
  ...props
}: React.HTMLAttributes<HTMLSpanElement> & {
  variant?: "default" | "success" | "warning" | "outline";
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        variant === "default" && "bg-brand/10 text-brand",
        variant === "success" && "bg-emerald-500/10 text-emerald-600",
        variant === "warning" && "bg-amber-500/10 text-amber-600",
        variant === "outline" && "border border-black/10 text-muted",
        className
      )}
      {...props}
    />
  );
}
