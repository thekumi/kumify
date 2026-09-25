function tryParseIds(str) {
  try { return JSON.parse(str).map(Number) } catch { return [] }
}

function moodId(s) {
  return s.mood_id != null ? Number(s.mood_id) : (s.mood != null ? Number(s.mood) : null)
}

function moodValue(s, moodMap) {
  const mid = moodId(s)
  if (mid == null) return null
  const v = Number(moodMap[mid]?.value)
  return isNaN(v) || v === 0 ? null : v
}

export function filterByDays(items, days, getTs = i => i.timestamp, end = null) {
  if (!days && !end) return items
  const endDate = end ? new Date(end + 'T23:59:59.999') : new Date()
  if (!days) return items
  const cutoff = new Date(endDate)
  cutoff.setDate(cutoff.getDate() - days)
  return items.filter(i => {
    const t = new Date(getTs(i))
    return t >= cutoff && t <= endDate
  })
}

export function moodOverTime(statuses, moodMap, days = 90, end = null) {
  const filtered = filterByDays(statuses, days, s => s.timestamp, end)
  const byDay = {}
  for (const s of filtered) {
    const day = new Date(s.timestamp).toISOString().slice(0, 10)
    const v = moodValue(s, moodMap)
    if (v == null) continue
    if (!byDay[day]) byDay[day] = []
    byDay[day].push(v)
  }
  return Object.entries(byDay)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([day, vals]) => ({ x: day, y: vals.reduce((a, b) => a + b, 0) / vals.length }))
}

export function moodDistribution(statuses, moodMap, days = 0, end = null) {
  const filtered = filterByDays(statuses, days, s => s.timestamp, end)
  const counts = {}
  for (const s of filtered) {
    const mid = moodId(s)
    if (mid == null) continue
    counts[mid] = (counts[mid] || 0) + 1
  }
  const entries = Object.entries(counts).sort(([, a], [, b]) => b - a)
  return {
    labels: entries.map(([mid]) => moodMap[mid]?.name ?? '?'),
    data: entries.map(([, c]) => c),
    colors: entries.map(([mid]) => moodMap[mid]?.color ?? '#a8a29e'),
  }
}

export function activityFrequency(statuses, activityMap, days = 0, end = null) {
  const filtered = filterByDays(statuses, days, s => s.timestamp, end)
  const counts = {}
  for (const s of filtered) {
    const ids = s.activity_ids ? tryParseIds(s.activity_ids) : (s.activities ?? []).map(a => a.id)
    for (const aid of ids) counts[aid] = (counts[aid] || 0) + 1
  }
  const entries = Object.entries(counts).sort(([, a], [, b]) => b - a).slice(0, 10)
  return {
    labels: entries.map(([aid]) => activityMap[aid]?.name ?? '?'),
    data: entries.map(([, c]) => c),
  }
}

export function entryCountByTimeOfDay(statuses, days = 0, end = null) {
  const filtered = filterByDays(statuses, days, s => s.timestamp, end)
  const labels = ['Night (0–6)', 'Morning (6–12)', 'Afternoon (12–18)', 'Evening (18–24)']
  const counts = [0, 0, 0, 0]
  for (const s of filtered) {
    const h = new Date(s.timestamp).getHours()
    counts[h < 6 ? 0 : h < 12 ? 1 : h < 18 ? 2 : 3]++
  }
  return { labels, data: counts }
}

export function calendarData(statuses, moodMap) {
  const days = {}
  for (const s of statuses) {
    const day = new Date(s.timestamp).toISOString().slice(0, 10)
    const v = moodValue(s, moodMap)
    if (!days[day]) days[day] = { count: 0, moods: [] }
    days[day].count++
    if (v != null) days[day].moods.push(v)
  }
  return Object.fromEntries(
    Object.entries(days).map(([d, { count, moods }]) => [d, {
      count,
      avgMood: moods.length ? moods.reduce((a, b) => a + b, 0) / moods.length : null,
    }])
  )
}

export function habitCompletionRates(habitLogs, habits, days = 0, end = null) {
  const now = end ? new Date(end + 'T23:59:59.999') : new Date()
  let cutoff = null
  if (days > 0) {
    cutoff = new Date(now)
    cutoff.setDate(cutoff.getDate() - days)
  }
  const filtered = cutoff
    ? habitLogs.filter(l => { const d = new Date(l.date); return d >= cutoff && d <= now })
    : habitLogs

  let totalDays
  if (days > 0) {
    totalDays = days
  } else if (habitLogs.length) {
    const first = habitLogs.reduce((min, l) => {
      const d = new Date(l.date); return d < min ? d : min
    }, now)
    totalDays = Math.max(1, Math.ceil((now - first) / 86400000))
  } else {
    totalDays = 1
  }

  const counts = {}
  for (const log of filtered) counts[log.habit] = (counts[log.habit] || 0) + 1

  function expected(habit) {
    const g = habit.goal
    if (!g) return totalDays
    if (g.period === 'daily')   return Math.max(1, Math.round(totalDays * g.target_count))
    if (g.period === 'weekly')  return Math.max(1, Math.round(totalDays / 7 * g.target_count))
    if (g.period === 'monthly') return Math.max(1, Math.round(totalDays / 30 * g.target_count))
    return totalDays
  }

  return habits
    .map(h => ({ id: h.id, name: h.name ?? '?', count: counts[h.id] || 0, expected: expected(h), totalDays }))
    .filter(h => h.count > 0)
    .sort((a, b) => (b.count / b.expected) - (a.count / a.expected))
}

export function dreamFrequency(dreams, days = 0, end = null) {
  const filtered = filterByDays(dreams, days, d => d.timestamp, end)
  if (!filtered.length) return { labels: [], data: [] }
  const useMonths = days === 0 || days > 100
  const byPeriod = {}
  for (const d of filtered) {
    const date = new Date(d.timestamp)
    let key
    if (useMonths) {
      key = date.toISOString().slice(0, 7)
    } else {
      const dow = date.getDay() === 0 ? 6 : date.getDay() - 1
      const monday = new Date(date)
      monday.setDate(date.getDate() - dow)
      key = monday.toISOString().slice(0, 10)
    }
    byPeriod[key] = (byPeriod[key] || 0) + 1
  }
  const entries = Object.entries(byPeriod).sort(([a], [b]) => a.localeCompare(b))
  return {
    labels: entries.map(([k]) =>
      useMonths
        ? new Date(k + '-01T12:00:00').toLocaleString('default', { month: 'short', year: 'numeric' })
        : new Date(k + 'T12:00:00').toLocaleDateString('default', { month: 'short', day: 'numeric' })
    ),
    data: entries.map(([, c]) => c),
  }
}

export function currentStreak(statuses) {
  if (!statuses.length) return 0
  const days = new Set(statuses.map(s => s.timestamp.slice(0, 10)))
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const todayStr = today.toISOString().slice(0, 10)
  const checkDate = new Date(today)
  if (!days.has(todayStr)) checkDate.setDate(checkDate.getDate() - 1)
  let streak = 0
  while (days.has(checkDate.toISOString().slice(0, 10))) {
    streak++
    checkDate.setDate(checkDate.getDate() - 1)
  }
  return streak
}

export function weekdayStats(statuses, moodMap, days = 0, end = null) {
  const filtered = filterByDays(statuses, days, s => s.timestamp, end)
  const labels   = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  const counts   = new Array(7).fill(0)
  const moodSums = new Array(7).fill(0)
  const moodN    = new Array(7).fill(0)
  for (const s of filtered) {
    const dow = new Date(s.timestamp).getDay()
    const i = dow === 0 ? 6 : dow - 1
    counts[i]++
    const mid = s.mood_id != null ? Number(s.mood_id) : (s.mood != null ? Number(s.mood) : null)
    if (mid != null) {
      const v = Number(moodMap[mid]?.value)
      if (!isNaN(v) && v !== 0) { moodSums[i] += v; moodN[i]++ }
    }
  }
  return {
    labels,
    counts,
    avgMoods: labels.map((_, i) => moodN[i] > 0 ? +(moodSums[i] / moodN[i]).toFixed(1) : null),
  }
}

export function propertyOverTime(statuses, propertyId, days = 0, end = null) {
  const filtered = filterByDays(statuses, days, s => s.timestamp, end)
  const byDay = {}
  for (const s of filtered) {
    const props = s.properties
    if (!props || props[propertyId] == null) continue
    const day = new Date(s.timestamp).toISOString().slice(0, 10)
    if (!byDay[day]) byDay[day] = []
    byDay[day].push(Number(props[propertyId]))
  }
  return Object.entries(byDay)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([day, vals]) => ({ x: day, y: vals.reduce((a, b) => a + b, 0) / vals.length }))
}

export function buildCalendarWeeks(weeks = 52) {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const dow = today.getDay() === 0 ? 6 : today.getDay() - 1
  const monday = new Date(today)
  monday.setDate(today.getDate() - dow)
  const start = new Date(monday)
  start.setDate(monday.getDate() - (weeks - 1) * 7)

  const grid = []
  for (let w = 0; w < weeks; w++) {
    const week = []
    for (let d = 0; d < 7; d++) {
      const day = new Date(start)
      day.setDate(start.getDate() + w * 7 + d)
      week.push(day.toISOString().slice(0, 10))
    }
    grid.push(week)
  }
  return grid
}
