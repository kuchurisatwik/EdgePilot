import Link from "next/link";

/** Placeholder. Real login/register forms + auth flow arrive in M1. */
export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <div className="w-full max-w-sm rounded-lg border border-border bg-panel p-8 text-center">
        <h1 className="text-lg font-semibold text-text">Trader Copilot AI</h1>
        <p className="mt-2 text-sm text-text-muted">
          Authentication arrives in M1. For now, head to the dashboard shell.
        </p>
        <Link
          href="/dashboard"
          className="mt-6 inline-flex items-center justify-center rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent/90"
        >
          Open dashboard
        </Link>
      </div>
    </div>
  );
}
