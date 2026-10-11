import { getPeople, createPerson } from '@/api/people'

export const CONTACTS_ENABLED_KEY = 'androidContacts'

export async function syncAndroidContacts(ks) {
  if (!window.Android?.getNewContacts) return

  const newContacts = JSON.parse(window.Android.getNewContacts())
  for (const c of newContacts) {
    if (!c.name) continue
    const fields = { name: c.name }
    if (c.email) fields.email = c.email
    if (c.phone) fields.phone = c.phone
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
      if (p.email) c.email = p.email
      if (p.phone) c.phone = p.phone
      return c
    })
  window.Android.syncContacts(JSON.stringify(contacts))
}
