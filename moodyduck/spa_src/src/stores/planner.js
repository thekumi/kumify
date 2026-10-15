import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getCalendars, createCalendar as apiCreateCalendar,
  updateCalendar as apiUpdateCalendar, deleteCalendar as apiDeleteCalendar,
  getTaskLists, createTaskList as apiCreateTaskList,
  updateTaskList as apiUpdateTaskList, deleteTaskList as apiDeleteTaskList,
} from '@/api/planner'

export const usePlannerStore = defineStore('planner', () => {
  const calendars = ref([])
  const taskLists = ref([])
  const loaded = ref(false)

  async function loadCalendars(ks) {
    const raw = await getCalendars()
    calendars.value = await ks.decryptAll(raw)
  }

  async function loadTaskLists(ks) {
    const raw = await getTaskLists()
    taskLists.value = await ks.decryptAll(raw)
  }

  async function load(ks) {
    await Promise.all([loadCalendars(ks), loadTaskLists(ks)])
    loaded.value = true
  }

  async function createCalendar(ks, { name, color = '#4A90D9' }) {
    const encrypted_payload = await ks.encryptPayload({ name })
    const raw = await apiCreateCalendar({ color, encrypted_payload })
    const dec = await ks.decrypt(raw)
    calendars.value = [...calendars.value, dec]
    return dec
  }

  async function updateCalendar(ks, id, fields) {
    const { name, ...rest } = fields
    const body = { ...rest }
    if (name !== undefined) {
      const existing = calendars.value.find(c => c.id === id)
      const basePayload = existing?.encrypted_payload
        ? (await ks.decrypt({ encrypted_payload: existing.encrypted_payload }))
        : {}
      const { encrypted_payload: _ep, ...baseFields } = basePayload
      body.encrypted_payload = await ks.encryptPayload({ ...baseFields, name })
    }
    const raw = await apiUpdateCalendar(id, body)
    const dec = await ks.decrypt(raw)
    calendars.value = calendars.value.map(c => c.id === id ? dec : c)
    return dec
  }

  async function deleteCalendar(id) {
    await apiDeleteCalendar(id)
    calendars.value = calendars.value.filter(c => c.id !== id)
  }

  async function createTaskList(ks, { name, color = '#4A90D9' }) {
    const encrypted_payload = await ks.encryptPayload({ name })
    const raw = await apiCreateTaskList({ color, encrypted_payload })
    const dec = await ks.decrypt(raw)
    taskLists.value = [...taskLists.value, dec]
    return dec
  }

  async function updateTaskList(ks, id, fields) {
    const { name, ...rest } = fields
    const body = { ...rest }
    if (name !== undefined) {
      const existing = taskLists.value.find(t => t.id === id)
      const basePayload = existing?.encrypted_payload
        ? (await ks.decrypt({ encrypted_payload: existing.encrypted_payload }))
        : {}
      const { encrypted_payload: _ep, ...baseFields } = basePayload
      body.encrypted_payload = await ks.encryptPayload({ ...baseFields, name })
    }
    const raw = await apiUpdateTaskList(id, body)
    const dec = await ks.decrypt(raw)
    taskLists.value = taskLists.value.map(t => t.id === id ? dec : t)
    return dec
  }

  async function deleteTaskList(id) {
    await apiDeleteTaskList(id)
    taskLists.value = taskLists.value.filter(t => t.id !== id)
  }

  return {
    calendars,
    taskLists,
    loaded,
    load,
    loadCalendars,
    loadTaskLists,
    createCalendar,
    updateCalendar,
    deleteCalendar,
    createTaskList,
    updateTaskList,
    deleteTaskList,
  }
})
