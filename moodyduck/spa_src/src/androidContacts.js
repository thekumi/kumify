import { getPeople, createPerson } from '@/api/people'

export const CONTACTS_ENABLED_KEY = 'androidContacts'

export async function syncAndroidContacts(ks) {
  if (!window.Android?.getNewContacts) return

  const newContacts = JSON.parse(window.Android.getNewContacts())
  for (const c of newContacts) {
    if (!c.name) continue
    const fields = {}
    for (const key of ['name', 'nickname', 'phones', 'emails', 'addresses', 'websites', 'notes', 'organization', 'title', 'birthday', 'birthday_monthday']) {
      const v = c[key]
      if (Array.isArray(v) ? v.length : v) fields[key] = v
    }
    const encrypted_payload = await ks.encryptPayload(fields)
    await createPerson({ encrypted_payload }).catch(() => {})
  }

  if (!window.Android?.syncContacts) return
  const all = await getPeople().catch(() => [])
  const decrypted = await ks.decryptAll(all)
  const contacts = decrypted
    .filter(p => p.name)
    .map(p => {
      const c = { id: p.id, name: p.name }
      for (const key of ['nickname', 'phones', 'emails', 'addresses', 'birthday', 'birthday_monthday', 'notes', 'organization', 'title', 'websites']) {
        const v = p[key]
        if (Array.isArray(v) ? v.length : v) c[key] = v
      }
      return c
    })
  window.Android.syncContacts(JSON.stringify(contacts))
}
