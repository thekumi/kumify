import { registerCalendarProvider } from '@/planner/registry'
import { getVaccinations, getMedications } from '@/api/health'
import { expandRRule } from '@/planner/rrule'

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

registerCalendarProvider('health.medications', async (ks, fromDate, toDate) => {
  const raw = await getMedications().catch(() => [])
  const meds = await ks.decryptAll(raw)
  const events = []

  for (const med of meds) {
    if (med.prn || !med.times?.length) continue

    const startDate = med.start || fromDate
    let occurrenceDates

    if (med.rrule) {
      const baseEvent = {
        id: `med:${med.id}`,
        rrule: med.rrule,
        start: startDate,
        end: med.end || null,
        all_day: true,
      }
      occurrenceDates = expandRRule(baseEvent, fromDate, toDate).map(e => e.start.slice(0, 10))
    } else {
      if (startDate < fromDate || startDate > toDate) continue
      occurrenceDates = [startDate]
    }

    for (const dateStr of occurrenceDates) {
      for (const timeStr of med.times) {
        events.push({
          id: `virtual:medication:${med.id}:${dateStr}:${timeStr}`,
          title: med.name || 'Medication',
          start: `${dateStr}T${timeStr}:00`,
          end: null,
          all_day: false,
          virtual_key: 'health.medications',
          virtual: true,
          meta: { icon: med.icon || 'ph ph-pill', dosage: med.dosage || null },
        })
      }
    }
  }

  return events
})
