import { registerTaskListProvider } from '@/planner/registry'
import { dbGetAll } from '@/lib/db'

function tryParseIds(val) {
  if (Array.isArray(val)) return val.map(Number)
  try { return JSON.parse(val).map(Number) } catch { return [] }
}

registerTaskListProvider('habits', async (ks) => {
  const today = new Date().toISOString().slice(0, 10)
  const [rawHabits, rawStatuses] = await Promise.all([
    dbGetAll('habits'),
    dbGetAll('statuses'),
  ])
  const habits = await ks.decryptAll(rawHabits)

  const activitiesToday = new Set()
  for (const s of rawStatuses) {
    if (!s.timestamp?.startsWith(today)) continue
    const ids = s.activity_ids ? tryParseIds(s.activity_ids) : (s.activities ?? []).map(a => a.id)
    for (const id of ids) activitiesToday.add(Number(id))
  }

  return habits.map(h => ({
    id: `virtual:habit:${h.id}`,
    title: h.name || '(habit)',
    done: h.negative
      ? !activitiesToday.has(Number(h.activity_id))
      : activitiesToday.has(Number(h.activity_id)),
    due_date: today,
    virtual_key: 'habits',
    virtual: true,
  }))
})
