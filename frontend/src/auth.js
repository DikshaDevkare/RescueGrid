import { jsx as _jsx } from "react/jsx-runtime";
import { createContext, useContext, useEffect, useState } from 'react';
import { api } from './api';
const A = createContext(null);
export function AuthProvider({ children }) { const [user, setUser] = useState(null); useEffect(() => { if (localStorage.getItem('rg-token'))
    api.get('/auth/me').then(r => setUser(r.data)).catch(() => localStorage.removeItem('rg-token')); }, []); const v = { user, async login(e, p, r) { const x = await api.post('/auth/login', { email: e, password: p, role: r }); localStorage.setItem('rg-token', x.data.access_token); setUser(x.data.user); return x.data.user; }, async register(x) { await api.post('/auth/register', x); }, logout() { localStorage.removeItem('rg-token'); setUser(null); } }; return _jsx(A.Provider, { value: v, children: children }); }
export const useAuth = () => { const x = useContext(A); if (!x)
    throw Error('auth'); return x; };
