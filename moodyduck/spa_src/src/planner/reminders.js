export function scheduleReminder(task, decryptedTitle) {
  if (!window.Android?.scheduleReminder || !task.reminder_at) return
  window.Android.scheduleReminder(JSON.stringify({
    id: `task-${task.id}`,
    timestamp: new Date(task.reminder_at).getTime(),
    title: decryptedTitle || 'Reminder',
    body: task.due_date ? `Due ${task.due_date}` : '',
  }))
}

export function cancelReminder(taskId) {
  window.Android?.cancelReminder?.(`task-${taskId}`)
}
