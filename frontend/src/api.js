import axios from 'axios';
export const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api', timeout: 8000 });
api.interceptors.request.use(c => { const t = localStorage.getItem('rg-token'); if (t)
    c.headers.Authorization = `Bearer ${t}`; return c; });
