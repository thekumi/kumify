import { registerCalendarProvider } from '@/planner/registry'
import { getVaccinations } from '@/api/health'

registerCalendarProvider('health.vaccinations', async (ks, fromDate, toDate) => {
  const raw = await getVaccinations().catch(() => [])
  const vaccinations = await ks.decryptAll(raw)
  return vaccinations
    .filter(v => v.next_due && v.next_due >= fromDate && v.next_due <= toDate)
    .map(v => ({
      id: `virtual:vaccination:${v.id}`,
      title: v.name ? `${v.name} due` : 'Vaccination due',
      start: v.next_due,
      end: null,
      all_day: true,
      virtual_key: 'health.vaccinations',
      virtual: true,
    }))
})

registerCalendarProvider('health.medications', async () => [])
