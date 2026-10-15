import { registerTaskListProvider } from '@/planner/registry'
import { getHabits, getAllHabitLogs } from '@/api/habits'

registerTaskListProvider('habits', async (ks) => {
  const today = new Date().toISOString().slice(0, 10)
  const [rawHabits, rawLogs] = await Promise.all([
    getHabits().catch(() => []),
    getAllHabitLogs().catch(() => []),
  ])
  const habits = await ks.decryptAll(rawHabits)
  const loggedToday = new Set(rawLogs.filter(l => l.date === today).map(l => String(l.habit)))

  return habits.map(h => ({
    id: `virtual:habit:${h.id}`,
    title: h.name || '(habit)',
    done: loggedToday.has(String(h.id)),
    due_date: today,
    virtual_key: 'habits',
    virtual: true,
  }))
})
