import axios from 'axios';
import { API_BASE_URL } from '../config';

/**
 * Centralized Axios instance for the Compliance Checker Tool.
 * base URL and timeout are configured here.
 */
const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 900000, // 15 minutes (Agentic LLM assessments can be very slow)
    headers: {
        'Content-Type': 'application/json',
    },
});

// Response interceptor for global error logging
api.interceptors.response.use(
    (response) => response,
    (error) => {
        const message = error.response?.data?.detail || error.message;
        console.error('API Error:', message);
        return Promise.reject(error);
    }
);

export default api;
