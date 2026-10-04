import { api } from './client'

export const getVapidPublicKey = () =>
  api.get('/vapid-public-key/')

export const getNotificationSettings = () =>
  api.get('/notification-settings/')

export const updateNotificationSettings = (data) =>
  api.patch('/notification-settings/', data)

export const registerPushSubscription = (sub) =>
  api.post('/push-subscriptions/', sub)

export const deletePushSubscription = (id) =>
  api.delete(`/push-subscriptions/${id}/`)

export const getPushSubscriptions = () =>
  api.getAll('/push-subscriptions/')
