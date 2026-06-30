"use client";

import { useRef } from "react";
import { AuthedImage } from "@/components/trades/AuthedImage";
import {
  useDeleteScreenshot,
  useScreenshots,
  useUploadScreenshot,
} from "@/hooks/useScreenshots";
import type { Screenshot, ScreenshotSlot } from "@/types";

const SLOTS: { slot: ScreenshotSlot; label: string }[] = [
  { slot: "entry_trade_tf", label: "Entry · Trade TF" },
  { slot: "entry_higher_tf", label: "Entry · Higher TF" },
  { slot: "exit_trade_tf", label: "Exit · Trade TF" },
  { slot: "exit_higher_tf", label: "Exit · Higher TF" },
];

function SlotCell({
  slot,
  label,
  shot,
  uploading,
  onUpload,
  onDelete,
}: {
  slot: ScreenshotSlot;
  label: string;
  shot?: Screenshot;
  uploading: boolean;
  onUpload: (slot: ScreenshotSlot, file: File) => void;
  onDelete: (id: string) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);

  return (
    <div className="rounded-md border border-border bg-panel-raised p-2">
      <div className="mb-1 flex items-center justify-between">
        <span className="text-[10px] uppercase tracking-wide text-text-muted">{label}</span>
        {shot ? (
          <button
            type="button"
            onClick={() => onDelete(shot.id)}
            className="text-[10px] text-text-muted hover:text-danger"
          >
            Delete
          </button>
        ) : null}
      </div>

      {shot ? (
        <AuthedImage url={shot.url} alt={label} />
      ) : (
        <div className="flex h-32 items-center justify-center rounded border border-dashed border-border text-xs text-text-muted">
          No image
        </div>
      )}

      <input
        ref={inputRef}
        type="file"
        accept="image/png,image/jpeg,image/webp"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) onUpload(slot, file);
          e.target.value = "";
        }}
      />
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        disabled={uploading}
        className="mt-2 w-full rounded border border-border py-1 text-xs text-text-muted hover:text-text disabled:opacity-50"
      >
        {shot ? "Replace" : "Upload"}
      </button>
    </div>
  );
}

export function ScreenshotGallery({ tradeId }: { tradeId: string }) {
  const { data: shots } = useScreenshots(tradeId);
  const upload = useUploadScreenshot(tradeId);
  const remove = useDeleteScreenshot(tradeId);
  const bySlot = new Map((shots ?? []).map((s) => [s.slot, s]));

  return (
    <section className="rounded-lg border border-border bg-panel p-5">
      <h2 className="mb-3 text-sm font-semibold text-text">Screenshots</h2>
      <div className="grid grid-cols-2 gap-2">
        {SLOTS.map(({ slot, label }) => (
          <SlotCell
            key={slot}
            slot={slot}
            label={label}
            shot={bySlot.get(slot)}
            uploading={upload.isPending}
            onUpload={(s, f) => upload.mutate({ slot: s, file: f })}
            onDelete={(id) => remove.mutate(id)}
          />
        ))}
      </div>
      <p className="mt-3 text-xs text-text-muted">
        PNG/JPEG/WebP, up to 5 MB. Stored locally; future AI chart analysis uses these.
      </p>
    </section>
  );
}
