import { registerCalendarProvider } from '@/planner/registry'
import { dbGetAll } from '@/lib/db'

registerCalendarProvider('friends.birthdays', async (ks, fromDate, toDate) => {
  const raw = await dbGetAll('people')
  const people = await ks.decryptAll(raw)

  const fromYear = new Date(fromDate).getFullYear()
  const toYear = new Date(toDate).getFullYear()
  const events = []

  for (const person of people) {
    const birthday = person.birthday
    if (!birthday) continue
    const parts = birthday.split('-')
    if (parts.length < 3) continue
    const [, mm, dd] = parts
    for (let year = fromYear - 1; year <= toYear + 1; year++) {
      const isoDate = `${year}-${mm}-${dd}`
      if (isoDate >= fromDate && isoDate <= toDate) {
        events.push({
          id: `virtual:birthday:${person.id}:${year}`,
          title: person.name || '(unknown)',
          start: isoDate,
          end: null,
          all_day: true,
          virtual_key: 'friends.birthdays',
          virtual: true,
        })
      }
    }
  }
  return events
})
