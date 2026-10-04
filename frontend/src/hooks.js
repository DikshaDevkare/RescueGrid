import { useEffect, useState } from 'react';
export const useOnline = () => { const [x, setX] = useState(navigator.onLine); useEffect(() => { const a = () => setX(true), b = () => setX(false); addEventListener('online', a); addEventListener('offline', b); return () => { removeEventListener('online', a); removeEventListener('offline', b); }; }, []); return x; };
export const useReveal = () => useEffect(() => { const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) {
    e.target.classList.add('show');
    io.unobserve(e.target);
} }), { threshold: .12 }); document.querySelectorAll('[data-reveal]').forEach(x => io.observe(x)); return () => io.disconnect(); }, []);
