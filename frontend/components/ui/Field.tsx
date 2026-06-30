import { forwardRef, type InputHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

type FieldProps = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  error?: string;
};

export const Field = forwardRef<HTMLInputElement, FieldProps>(function Field(
  { label, error, className, ...props },
  ref,
) {
  return (
    <label className="block space-y-1">
      <span className="text-xs font-medium text-text-muted">{label}</span>
      <input
        ref={ref}
        className={cn(
          "w-full rounded-md border border-border bg-panel-raised px-3 py-2 text-sm text-text outline-none transition-colors focus:border-accent",
          error && "border-danger",
          className,
        )}
        {...props}
      />
      {error ? <span className="block text-xs text-danger">{error}</span> : null}
    </label>
  );
});
