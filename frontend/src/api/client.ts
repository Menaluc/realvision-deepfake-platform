// Error body the backend sends for every failed request except /api/health
interface ApiErrorBody {
    error?: { code?: string; message?: string };
}

// Sends a request to the API and returns the parsed JSON body,
// throwing the server's error message (or fallbackError) when the response is not OK
export async function requestJson<T>(url: string, init?: RequestInit, fallbackError = "Request failed"): Promise<T> {
    const response = await fetch(url, init);

    // Checked before parsing: an error may not be JSON at all
    // (for example a 502 page from the dev proxy when the backend is down)
    if (!response.ok) {
        throw new Error(await readErrorMessage(response) ?? fallbackError);
    }

    return await response.json() as T;
}

async function readErrorMessage(response: Response): Promise<string | null> {
    try {
        const body = await response.json() as ApiErrorBody;
        return body.error?.message ?? null;
    } catch {
        return null;
    }
}
