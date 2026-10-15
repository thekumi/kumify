const BYDAY_JS = { MO: 1, TU: 2, WE: 3, TH: 4, FR: 5, SA: 6, SU: 0 }

function parseRRule(rrule) {
  return Object.fromEntries(rrule.split(';').map(p => {
    const eq = p.indexOf('=')
    return [p.slice(0, eq), p.slice(eq + 1)]
  }))
}

export function expandRRule(event, fromIso, toIso) {
  if (!event.rrule) return []
  const r = parseRRule(event.rrule)
  const freq = r.FREQ
  if (!freq) return []

  const from = new Date(fromIso + 'T00:00:00')
  const to = new Date(toIso + 'T23:59:59')
  const dtStart = new Date(event.all_day ? event.start + 'T00:00:00' : event.start)
  const durMs = event.end
    ? new Date(event.all_day ? event.end + 'T00:00:00' : event.end).getTime() - dtStart.getTime()
    : 0
  const maxCount = r.COUNT ? +r.COUNT : 999
  const untilDate = r.UNTIL
    ? new Date(r.UNTIL.length >= 8
        ? r.UNTIL.slice(0, 4) + '-' + r.UNTIL.slice(4, 6) + '-' + r.UNTIL.slice(6, 8)
        : r.UNTIL)
    : null
  const bydays = r.BYDAY
    ? r.BYDAY.split(',').map(s => BYDAY_JS[s.slice(-2)]).filter(n => n !== undefined)
    : null

  function makeOcc(d) {
    const s = event.all_day ? d.toISOString().slice(0, 10) : d.toISOString()
    const e = durMs
      ? (event.all_day
          ? new Date(d.getTime() + durMs).toISOString().slice(0, 10)
          : new Date(d.getTime() + durMs).toISOString())
      : null
    return { ...event, id: `${event.id}:${d.toISOString().slice(0, 10)}`, start: s, end: e, _expanded: true }
  }

  const results = []
  let n = 0

  if (bydays && freq === 'WEEKLY') {
    const cursor = new Date(Math.max(from.getTime(), dtStart.getTime()))
    while (cursor <= to && n < maxCount) {
      if (untilDate && cursor > untilDate) break
      if (bydays.includes(cursor.getDay())) {
        results.push(makeOcc(cursor))
        n++
      }
      cursor.setDate(cursor.getDate() + 1)
    }
    return results
  }

  const anchor = new Date(dtStart)
  if (anchor < from) {
    if (freq === 'DAILY') {
      const skip = Math.max(0, Math.floor((from.getTime() - anchor.getTime()) / 864e5) - 1)
      anchor.setDate(anchor.getDate() + skip)
    } else if (freq === 'WEEKLY') {
      const skip = Math.max(0, Math.floor((from.getTime() - anchor.getTime()) / (7 * 864e5)) - 1)
      anchor.setDate(anchor.getDate() + skip * 7)
    } else if (freq === 'MONTHLY') {
      const skip = Math.max(0, (from.getFullYear() - anchor.getFullYear()) * 12 + from.getMonth() - anchor.getMonth() - 1)
      if (skip > 0) anchor.setMonth(anchor.getMonth() + skip)
    } else if (freq === 'YEARLY') {
      const skip = Math.max(0, from.getFullYear() - anchor.getFullYear() - 1)
      if (skip > 0) anchor.setFullYear(anchor.getFullYear() + skip)
    }
  }

  while (anchor <= to && n < maxCount) {
    if (untilDate && anchor > untilDate) break
    if (anchor >= from) {
      results.push(makeOcc(anchor))
      n++
    }
    if (freq === 'DAILY') anchor.setDate(anchor.getDate() + 1)
    else if (freq === 'WEEKLY') anchor.setDate(anchor.getDate() + 7)
    else if (freq === 'MONTHLY') anchor.setMonth(anchor.getMonth() + 1)
    else if (freq === 'YEARLY') anchor.setFullYear(anchor.getFullYear() + 1)
    else break
  }

  return results
}
