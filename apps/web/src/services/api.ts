import { ProcessRequest, ProcessResponse } from "../types";

const API_BASE_URL = "http://localhost:8000";

export class ApiError extends Error {
  constructor(message: string, public status: number, public response?: any) {
    super(message);
    this.name = "ApiError";
  }
}

export const apiClient = {
  async processRequest(request: ProcessRequest): Promise<ProcessResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/process`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new ApiError(
          errorData.detail || `HTTP error! status: ${response.status}`,
          response.status,
          errorData
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }

      if (error instanceof TypeError && error.message.includes("fetch")) {
        throw new ApiError(
          "Unable to connect to the server. Please ensure the backend is running on localhost:8000.",
          0
        );
      }

      throw new ApiError(
        error instanceof Error ? error.message : "Unknown error occurred",
        0
      );
    }
  },

  async healthCheck(): Promise<{
    status: string;
    timestamp: string;
    version: string;
  }> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);

      if (!response.ok) {
        throw new ApiError(
          `Health check failed: ${response.status}`,
          response.status
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }

      throw new ApiError(
        error instanceof Error ? error.message : "Health check failed",
        0
      );
    }
  },
};
