import { api } from '@/api/client'
import {
  dbClear,
  dbDeleteMany,
  dbPutMany,
  getSyncMeta,
  setSyncMeta,
} from './db'

// Resources included in sync. `store` must match the IndexedDB store name and
// the `resource_type` values written to DeletionLog on the server.
const RESOURCES = [
  { store: 'statuses',           path: '/statuses/',                      paginated: true  },
  { store: 'moods',              path: '/moods/',                         paginated: false },
  { store: 'activities',         path: '/activities/?include_hidden=true', paginated: false },
  { store: 'activity_categories',path: '/activity-categories/',           paginated: false },
  { store: 'dreams',             path: '/dreams/',                        paginated: true  },
  { store: 'habits',             path: '/habits/',                        paginated: false },
  { store: 'health_logs',        path: '/health/logs/',                   paginated: true  },
  { store: 'cbt_records',        path: '/cbt/records/',                   paginated: true  },
  { store: 'health_parameters',  path: '/health/parameters/',             paginated: false },
  { store: 'medications',        path: '/health/medications/',            paginated: false },
  { store: 'vaccinations',       path: '/health/vaccinations/',           paginated: false },
  { store: 'people',             path: '/friends/',                       paginated: false },
  { store: 'properties',         path: '/properties/',                    paginated: false },
]

// Subtract 5 seconds as a clock-skew buffer so we never miss a record.
function sinceParam(isoString) {
  return new Date(new Date(isoString) - 5000).toISOString()
}

let _syncInProgress = false
let _syncCallbacks = []

export function onSyncComplete(fn) {
  _syncCallbacks.push(fn)
}

export function offSyncComplete(fn) {
  _syncCallbacks = _syncCallbacks.filter(f => f !== fn)
}

export async function sync({ force = false } = {}) {
  if (_syncInProgress) return
  _syncInProgress = true
  try {
    const lastSync = await getSyncMeta('last_sync')
    const since = force ? null : lastSync
    const syncTime = new Date().toISOString()

    await Promise.all(RESOURCES.map(r => _syncResource(r, since)))

    if (since) {
      await _applyDeletions(since)
    }

    await setSyncMeta('last_sync', syncTime)
    _syncCallbacks.forEach(fn => fn())
  } catch (e) {
    console.warn('[sync] sync failed:', e)
  } finally {
    _syncInProgress = false
  }
}

async function _syncResource(resource, since) {
  try {
    let path = resource.path
    if (since) {
      const sep = path.includes('?') ? '&' : '?'
      path = `${path}${sep}since=${encodeURIComponent(sinceParam(since))}`
    }
    const items = await api.getAll(path)

    if (since) {
      await dbPutMany(resource.store, items)
    } else {
      await dbClear(resource.store)
      await dbPutMany(resource.store, items)
    }
  } catch (e) {
    console.warn(`[sync] failed to sync ${resource.store}:`, e)
  }
}

async function _applyDeletions(since) {
  try {
    const deletions = await api.get(
      `/sync/deletions/?since=${encodeURIComponent(sinceParam(since))}`
    )
    const byStore = {}
    for (const d of deletions) {
      if (!byStore[d.resource_type]) byStore[d.resource_type] = []
      byStore[d.resource_type].push(d.resource_id)
    }
    await Promise.all(
      Object.entries(byStore).map(([store, ids]) => dbDeleteMany(store, ids))
    )
  } catch (e) {
    console.warn('[sync] failed to apply deletions:', e)
  }
}

export async function getLastSync() {
  return getSyncMeta('last_sync')
}

export function isSyncing() {
  return _syncInProgress
}
