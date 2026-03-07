// Central API configuration
// In development: defaults to localhost:8000
// In production (Render): set VITE_API_URL in the environment
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
