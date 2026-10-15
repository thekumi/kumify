import { getEvents } from '@/api/planner'

export async function syncCalendarsToSystem(ks, plannerStore) {
  if (!window.Android?.syncCalendarEvents) return
  const syncCals = plannerStore.calendars.filter(c => !c.virtual_key && c.sync_to_system)
  if (!syncCals.length) return

  const today = new Date()
  const from = new Date(today)
  from.setDate(from.getDate() - 30)
  const to = new Date(today)
  to.setDate(to.getDate() + 180)
  const fromIso = from.toISOString().slice(0, 10)
  const toIso = to.toISOString().slice(0, 10)

  const rawEvents = await getEvents({ from: fromIso, to: toIso })
  const events = await ks.decryptAll(rawEvents)

  for (const cal of syncCals) {
    const calEvents = events.filter(ev => ev.calendar === cal.id)
    window.Android.syncCalendarEvents(JSON.stringify({
      calendar_id: cal.id,
      calendar_name: cal.name || 'MoodyDuck',
      color: cal.color || '#6366F1',
      events: calEvents.map(ev => ({
        id: ev.id,
        title: ev.title || '(event)',
        start_ms: new Date(ev.all_day ? ev.start + 'T00:00:00' : ev.start).getTime(),
        end_ms: ev.end
          ? new Date(ev.all_day ? ev.end + 'T00:00:00' : ev.end).getTime()
          : null,
        all_day: ev.all_day ?? false,
        rrule: ev.rrule ?? null,
      })),
    }))
  }
}

export function removeSystemCalendar(calendarId) {
  window.Android?.removeSystemCalendar?.(calendarId)
}
