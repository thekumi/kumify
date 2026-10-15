const _calendarProviders = new Map()
const _taskListProviders = new Map()

export function registerCalendarProvider(virtualKey, fetchFn) {
  _calendarProviders.set(virtualKey, fetchFn)
}

export function registerTaskListProvider(virtualKey, fetchFn) {
  _taskListProviders.set(virtualKey, fetchFn)
}

export function getCalendarProvider(virtualKey) {
  return _calendarProviders.get(virtualKey) ?? null
}

export function getTaskListProvider(virtualKey) {
  return _taskListProviders.get(virtualKey) ?? null
}
