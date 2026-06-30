"use client";

import { useEffect, useState } from "react";
import { api } from "@/services/apiClient";

/** Loads an auth-protected image as a Blob and renders it via an object URL. */
export function AuthedImage({ url, alt }: { url: string; alt: string }) {
  const [src, setSrc] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    let objectUrl: string | null = null;
    api
      .blob(url)
      .then((blob) => {
        if (!active) return;
        objectUrl = URL.createObjectURL(blob);
        setSrc(objectUrl);
      })
      .catch(() => {});
    return () => {
      active = false;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [url]);

  if (!src) {
    return <div className="flex h-32 items-center justify-center text-xs text-text-muted">Loading…</div>;
  }
  // Object URL of a user-uploaded blob; next/image can't optimize it.
  // eslint-disable-next-line @next/next/no-img-element
  return <img src={src} alt={alt} className="h-32 w-full rounded object-cover" />;
}
