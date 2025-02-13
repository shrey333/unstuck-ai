export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class APIError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = 'APIError';
  }
}

const handleResponse = async (response: Response) => {
  if (!response.ok) {
    // Clear session on 401 (Unauthorized) or 403 (Forbidden)
    if (response.status === 401 || response.status === 403) {
      document.cookie = "chat_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    }
    
    throw new APIError(
      response.statusText || 'An error occurred',
      response.status
    );
  }
  return response.json();
};

export async function uploadFiles(files: FileList): Promise<{ total_chunks: number }> {
  const formData = new FormData();
  Array.from(files).forEach((file) => formData.append("files", file));

  try {
    const response = await fetch(`${API_URL}/api/v1/documents/upload`, {
      method: "POST",
      credentials: "include",
      body: formData,
    });
    return handleResponse(response);
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError('Failed to upload files', 500);
  }
}

export async function askQuestion(question: string) {
  try {
    const response = await fetch(`${API_URL}/api/v1/queries/ask`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({ question }),
    });
    return handleResponse(response);
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError('Failed to get answer', 500);
  }
}
