// Client-side staging runner: fetches all unencrypted records from /api/staging/,
// encrypts them, and PATCHes them back. Also encrypts any plaintext media files.
// Runs automatically once per session from bootstrap.js after the key is ready.
// Can also be triggered manually: window.keystore.runStaging()

import { apiFetch, getCsrfToken } from "./util.js";

export async function runStaging() {
  const dataKey = await window.keystore.ready;
  if (!dataKey) {
    console.warn("[staging] No data key available — skipping staging.");
    return { skipped: true };
  }

  const res = await apiFetch("GET", "/api/staging/");
  if (!res.ok) throw new Error(`Staging fetch failed: ${res.status}`);
  const staging = await res.json();

  // Determine which fields to encrypt per model type
  const MODEL_FIELDS = {
    statuses:     ["title", "text"],
    moods:        ["name", "value", "color", "icon"],
    activities:   ["name", "icon"],
    dreams:       ["title", "content"],
    cbt_records:  ["title", "situation", "thoughts", "pro_facts", "con_facts", "realistic", "outcome"],
    health_logs:  ["notes"],
    vaccinations: ["name", "target_disease", "provider", "batch_number", "notes"],
  };

  const patch = {};
  let total = 0;

  for (const [key, fields] of Object.entries(MODEL_FIELDS)) {
    const records = staging[key] ?? [];
    if (!records.length) continue;

    patch[key] = [];
    for (const record of records) {
      const plainFields = {};
      for (const field of fields) {
        if (record[field] !== null && record[field] !== undefined && record[field] !== "") {
          plainFields[field] = String(record[field]);
        }
      }
      if (Object.keys(plainFields).length === 0) continue;

      const encrypted_payload = await window.keystore.encryptPayload(dataKey, plainFields);
      patch[key].push({ id: record.id, encrypted_payload });
      total++;
    }
  }

  if (total > 0) {
    const patchRes = await apiFetch("PATCH", "/api/staging/", patch);
    if (!patchRes.ok && patchRes.status !== 207) {
      throw new Error(`Staging PATCH failed: ${patchRes.status}`);
    }
    const result = await patchRes.json();
    console.info(`[staging] Encrypted ${result.updated} text records.`);
  }

  // Encrypt plaintext media files
  let mediaTotal = 0;
  for (const [key, endpoint] of [
    ["status_media", "/api/media/status/"],
    ["dream_media", "/api/media/dream/"],
  ]) {
    const items = staging[key] ?? [];
    for (const item of items) {
      try {
        const fileRes = await fetch(item.url, { credentials: "same-origin" });
        if (!fileRes.ok) { console.warn("[staging] could not fetch media", item.url); continue; }
        const mimeType = fileRes.headers.get("content-type") || "application/octet-stream";
        const filename = item.url.split("/").pop().split("?")[0].replace(/\.enc$/, "");
        const buf = await fileRes.arrayBuffer();

        const iv = crypto.getRandomValues(new Uint8Array(12));
        const ct = await crypto.subtle.encrypt({ name: "AES-GCM", iv }, dataKey, buf);
        const combined = new Uint8Array(12 + ct.byteLength);
        combined.set(iv, 0);
        combined.set(new Uint8Array(ct), 12);

        const encMeta = await window.keystore.encryptPayload(dataKey, { filename, mime_type: mimeType });

        const fd = new FormData();
        fd.append("file", new Blob([combined], { type: "application/octet-stream" }), filename + ".enc");
        fd.append("encrypted_payload", JSON.stringify(encMeta));
        await apiFetch("PATCH", `${endpoint}${item.id}/`, fd);
        mediaTotal++;
      } catch (e) {
        console.warn("[staging] media encrypt failed for", item.id, e);
      }
    }
  }

  if (mediaTotal > 0) console.info(`[staging] Encrypted ${mediaTotal} media files.`);

  return { updated: total, media: mediaTotal };
}

// Expose on window.keystore once ready
if (window.keystore) {
  window.keystore.runStaging = runStaging;
} else {
  window.addEventListener("keystore:ready", () => {
    window.keystore.runStaging = runStaging;
  });
}
