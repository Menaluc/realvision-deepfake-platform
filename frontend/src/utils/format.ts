export function formatBytes(bytes: number): string {
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}

export function formatDuration(seconds: number | null): string {
    if (seconds === null || isNaN(seconds)) return "—";
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60).toString().padStart(2, "0");
    return m + ":" + s;
}

export function formatPercent(value: number): string {
    return Math.round(value * 100) + "%";
}

// "video/mp4" → "MP4"
export function formatFileType(mimeType: string): string {
    return (mimeType || "video").split("/")[1]?.toUpperCase() || "—";
}

// Position in the video, e.g. 2.5 → "2.5s"
export function formatTimestamp(seconds: number | null): string {
    if (seconds === null) return "—";
    return seconds.toFixed(1) + "s";
}
