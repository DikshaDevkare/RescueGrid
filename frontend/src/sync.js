import { api } from './api';
import { db, DEVICE_ID, logActivity } from './db';
let busy = false;
export async function queue(entity, id, operation, payload, baseVersion = 0) { await db.pending.add({ id: crypto.randomUUID(), entity, entityId: id, operation, payload, baseVersion, deviceId: DEVICE_ID, createdAt: new Date().toISOString(), status: 'pending' }); await logActivity(`${operation} ${entity} ${id} queued`, 'queue'); if (navigator.onLine)
    syncNow(); }
export async function syncNow() { if (busy || !navigator.onLine)
    return; busy = true; try {
    for (const o of await db.pending.where('status').anyOf('pending', 'failed').sortBy('createdAt')) {
        await db.pending.update(o.id, { status: 'syncing' });
        try {
            const r = await api.post('/sync', { ...o, entity_id: o.entityId, base_version: o.baseVersion, device_id: o.deviceId });
            if (r.data.conflict) {
                await db.pending.update(o.id, { status: 'conflict' });
                await db.conflicts.put(r.data.conflict);
                await logActivity(`Conflict detected for ${o.entity} ${o.entityId}`, 'conflict');
            }
            else {
                await db.pending.delete(o.id);
                if (r.data.record) {
                    if (o.entity === 'victim')
                        await db.victims.put(r.data.record);
                    if (o.entity === 'incident')
                        await db.incidents.put(r.data.record);
                    if (o.entity === 'resource')
                        await db.resources.put(r.data.record);
                }
                await logActivity(`${o.operation} ${o.entity} synchronized`, 'sync');
            }
        }
        catch (e) {
            await db.pending.update(o.id, { status: 'failed', error: e?.response?.data?.detail || 'Sync failed' });
        }
    }
}
finally {
    busy = false;
} }
export function autoSync() { const f = () => syncNow(); window.addEventListener('online', f); const i = setInterval(f, 12000); return () => { window.removeEventListener('online', f); clearInterval(i); }; }
