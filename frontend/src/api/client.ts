// Sends a request to the API and returns the parsed JSON body,
// throwing the server's error message (or fallbackError) when the response is not OK
export async function requestJson<T>(url: string, init?: RequestInit, fallbackError = "Request failed"): Promise<T> {
    const response = await fetch(url, init);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || fallbackError);
    }

    return data as T;
}
