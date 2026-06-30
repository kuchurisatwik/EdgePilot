import { EmptyState } from "@/components/feedback/EmptyState";

/** Generic milestone placeholder used by route shells until each phase ships. */
export function PagePlaceholder({
  title,
  phase,
  description,
}: {
  title: string;
  phase: string;
  description: string;
}) {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold text-text">{title}</h1>
        <p className="text-sm text-text-muted">{description}</p>
      </div>
      <EmptyState
        title={`${title} — coming in ${phase}`}
        description="The application is being built phase by phase. This screen's shell is in place; its data is wired in the milestone above."
      />
    </div>
  );
}
