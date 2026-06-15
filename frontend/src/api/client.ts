import axios from "axios";

export const API_BASE_URL = "http://127.0.0.1:8001";

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json"
  }
});

export type LoginRequest = {
  username: string;
  password: string;
};

export type RegisterRequest = {
  username: string;
  password: string;
};

export type AnalyzeRequest = {
  text?: string;
  input_text?: string;
  log_text?: string;
  alert_text?: string;
};

export async function healthCheck() {
  const response = await api.get("/health");
  return response.data;
}

export async function login(payload: LoginRequest) {
  const response = await api.post("/auth/login", payload);
  return response.data;
}

export async function registerUser(payload: RegisterRequest) {
  const response = await api.post("/auth/register", payload);
  return response.data;
}

export async function getDashboardStats() {
  const response = await api.get("/dashboard/stats");
  return response.data;
}

export async function getCases() {
  const response = await api.get("/cases");
  return response.data;
}

export async function analyzeSOC(payload: AnalyzeRequest) {
  const response = await api.post("/soc/analyze", payload);
  return response.data;
}

export async function generateRCA(payload: AnalyzeRequest) {
  const response = await api.post("/rca/generate", payload);
  return response.data;
}

export async function mapGRC(payload: AnalyzeRequest) {
  const response = await api.post("/grc/map", payload);
  return response.data;
}