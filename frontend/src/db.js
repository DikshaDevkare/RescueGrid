import Dexie from 'dexie';
export const DEVICE_ID = localStorage.getItem('rg-device') || (() => { const x = crypto.randomUUID(); localStorage.setItem('rg-device', x); return x; })();
class DB extends Dexie {
    victims;
    incidents;
    resources;
    pending;
    conflicts;
    activities;
    constructor() { super('rescuegrid'); this.version(2).stores({ victims: 'id,severity,status,updated_at', incidents: 'id,severity,status,type,updated_at', resources: 'id,category,status,updated_at', pending: 'id,entity,entityId,status,createdAt', conflicts: 'id,entity,resolved,created_at', activities: '++id,createdAt,type' }); }
}
export const db = new DB();
export async function logActivity(text, type = 'info') { await db.activities.add({ text, type, createdAt: new Date().toISOString() }); }
