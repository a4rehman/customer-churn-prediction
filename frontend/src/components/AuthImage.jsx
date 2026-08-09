import { useEffect, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "/api";

export default function AuthImage({ src, alt = "", className = "" }) {
  const [url, setUrl] = useState(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let cancelled = false;
    let objectUrl = null;
    const token = localStorage.getItem("churniq_token");

    (async () => {
      try {
        const response = await fetch(`${API_URL}${src}`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
        if (!response.ok) throw new Error("load failed");
        const blob = await response.blob();
        objectUrl = URL.createObjectURL(blob);
        if (!cancelled) setUrl(objectUrl);
      } catch {
        if (!cancelled) setFailed(true);
      }
    })();

    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [src]);

  if (failed) {
    return <div className="h-40 flex items-center justify-center text-sm text-slate-500">Image unavailable</div>;
  }
  if (!url) {
    return <div className="h-40 animate-pulse bg-slate-800/50 rounded-lg" />;
  }
  return <img src={url} alt={alt} className={className} />;
}
