export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "APIError";
  }
}

export async function uploadFiles(files: FileList): Promise<{ total_chunks: number }> {
  const formData = new FormData();
  Array.from(files).forEach((file) => formData.append("files", file));

  const response = await fetch(`${API_URL}/api/v1/documents/upload`, {
    method: "POST",
    credentials: "include",
    body: formData,
  });

  if (!response.ok) {
    throw new APIError(response.status, `HTTP error ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

export async function askQuestion(question: string) {
  const response = await fetch(`${API_URL}/api/v1/queries/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    throw new APIError(response.status, `HTTP error ${response.status}: ${response.statusText}`);
  }

  return response.json();
}
