"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Field } from "@/components/ui/Field";
import { useAuth } from "@/features/auth/AuthContext";
import { useSettings, useUpdateSettings } from "@/hooks/useSettings";
import { toNumber } from "@/lib/format";
import { settingsApi } from "@/services/settingsApi";

const schema = z.object({
  name: z.string().min(1, "Name is required"),
  account_size: z.number().min(0, "Must be 0 or more"),
  default_risk_pct: z.number().gt(0, "Must be greater than 0").max(100, "Max 100%"),
});
type Values = z.infer<typeof schema>;

export default function SettingsPage() {
  const { user, refreshUser } = useAuth();
  const { data: settings, isLoading } = useSettings();
  const updateSettings = useUpdateSettings();
  const updateProfile = useMutation({ mutationFn: settingsApi.updateProfile });
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting, isDirty },
  } = useForm<Values>({
    resolver: zodResolver(schema),
    values:
      settings && user
        ? {
            name: user.name,
            account_size: toNumber(settings.account_size),
            default_risk_pct: toNumber(settings.default_risk_pct),
          }
        : undefined,
  });

  async function onSubmit(values: Values) {
    setError(null);
    setSaved(false);
    try {
      await updateSettings.mutateAsync({
        account_size: values.account_size,
        default_risk_pct: values.default_risk_pct,
      });
      if (values.name !== user?.name) {
        await updateProfile.mutateAsync({ name: values.name });
        await refreshUser();
      }
      setSaved(true);
    } catch {
      setError("Could not save settings. Please try again.");
    }
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-text">Settings</h1>
        <p className="text-sm text-text-muted">
          Your profile and the account size + default risk the Risk Engine uses.
        </p>
      </div>

      {isLoading ? (
        <p className="text-sm text-text-muted">Loading…</p>
      ) : (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <section className="rounded-lg border border-border bg-panel p-5">
            <h2 className="mb-4 text-sm font-semibold text-text">Profile</h2>
            <div className="space-y-4">
              <Field label="Name" error={errors.name?.message} {...register("name")} />
              <div>
                <p className="text-xs font-medium text-text-muted">Email</p>
                <p className="mt-1 text-sm text-text">{user?.email}</p>
              </div>
            </div>
          </section>

          <section className="rounded-lg border border-border bg-panel p-5">
            <h2 className="mb-1 text-sm font-semibold text-text">Account</h2>
            <p className="mb-4 text-xs text-text-muted">
              Quote currency: {settings?.quote_currency ?? "USDT"} (crypto MVP)
            </p>
            <div className="grid gap-4 sm:grid-cols-2">
              <Field
                label={`Account size (${settings?.quote_currency ?? "USDT"})`}
                type="number"
                step="any"
                error={errors.account_size?.message}
                {...register("account_size", { valueAsNumber: true })}
              />
              <Field
                label="Default risk per trade (%)"
                type="number"
                step="0.1"
                error={errors.default_risk_pct?.message}
                {...register("default_risk_pct", { valueAsNumber: true })}
              />
            </div>
          </section>

          <div className="flex items-center gap-3">
            <button
              type="submit"
              disabled={isSubmitting || !isDirty}
              className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent/90 disabled:opacity-60"
            >
              {isSubmitting ? "Saving…" : "Save changes"}
            </button>
            {saved ? <span className="text-sm text-success">Saved.</span> : null}
            {error ? <span className="text-sm text-danger">{error}</span> : null}
          </div>
        </form>
      )}

      <p className="text-xs text-text-muted">
        Strategies (M2) and Risk Rules (M4) will appear here in later phases.
      </p>
    </div>
  );
}
