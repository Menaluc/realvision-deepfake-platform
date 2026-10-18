// 20 MB counted as MiB, the same number as max_upload_bytes in
// backend/app/config.py. The server enforces it; checking here only saves
// uploading a file that would be rejected.
export const MAX_UPLOAD_BYTES = 20 * 1024 * 1024;

// Same text as the server's VIDEO_TOO_LARGE message
export const VIDEO_TOO_LARGE_MESSAGE = "The video is larger than the 20 MB limit.";
