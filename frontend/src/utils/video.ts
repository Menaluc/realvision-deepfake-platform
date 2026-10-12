// Reads a video file's duration (in seconds) from its metadata
export function readDuration(file: File): Promise<number | null> {
    return new Promise((resolve) => {
        const v = document.createElement("video");
        v.preload = "metadata";
        v.onloadedmetadata = () => {
            URL.revokeObjectURL(v.src);
            resolve(v.duration);
        };
        v.onerror = () => resolve(null);
        v.src = URL.createObjectURL(file);
    });
}
