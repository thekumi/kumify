import { apiFetch } from "./util.js";
import { getDeviceRecord, putDeviceRecord } from "./db.js";
import { generateDeviceKeyPair, exportPublicKey, importPublicKey } from "./device.js";
import { generateDataKey, wrapDataKey, unwrapDataKey } from "./datakey.js";
import { unwrapDataKeyFromBackup } from "./backup.js";
import { encryptField, decryptField, encryptPayload, decryptPayload } from "./fields.js";
import { encryptFile, decryptFileBuffer, decryptMediaUrl } from "./media.js";
import { promptPassphrase, showWaitingBanner } from "./ui.js";
import {
  generateUserKeyPair,
  exportUserPublicKey,
  wrapUserPrivateKey,
  unwrapUserPrivateKey,
  decryptECIES,
} from "./userkey.js";
import { runStaging } from "./staging.js";

let _dataKey = null;
let _userPrivateKey = null;

let _readyResolve;
const ready = new Promise((resolve) => {
  _readyResolve = resolve;
});

export { encryptField, decryptField, encryptPayload, decryptPayload, decryptECIES };
export const getDataKey = () => _dataKey;
export const getUserPrivateKey = () => _userPrivateKey;

async function registerDevice() {
  const keyPair = await generateDeviceKeyPair();
  const publicKeyB64 = await exportPublicKey(keyPair.publicKey);
  const label = navigator.userAgent.substring(0, 255);

  const res = await apiFetch("POST", "/api/devices/", {
    public_key: publicKeyB64,
    label,
  });
  if (!res.ok) throw new Error("Device registration failed");

  const device = await res.json();
  const record = {
    device_id: device.device_id,
    private_key: keyPair.privateKey,
    public_key_b64: publicKeyB64,
    data_key: null,
  };
  await putDeviceRecord(record);
  return record;
}

async function obtainDataKey(record, deviceState) {
  if (deviceState.encrypted_data_key) {
    const key = await unwrapDataKey(deviceState.encrypted_data_key, record.private_key);
    await wrapAndRegisterForSelf(record, key);
    return key;
  }

  const backupRes = await apiFetch("GET", "/api/keybackup/");
  if (backupRes.ok) {
    const backup = await backupRes.json();
    const key = await promptPassphrase((passphrase) =>
      unwrapDataKeyFromBackup(backup.encrypted_data_key, backup.kdf_salt, passphrase)
    );
    await wrapAndRegisterForSelf(record, key);
    return key;
  }

  const devicesRes = await apiFetch("GET", "/api/devices/");
  if (devicesRes.ok) {
    const { results: devices } = await devicesRes.json();
    const othersWithKey = devices.filter(
      (d) => d.device_id !== record.device_id && d.has_data_key
    );
    if (othersWithKey.length > 0) {
      showWaitingBanner();
      return null;
    }
  }

  const key = await generateDataKey();
  await wrapAndRegisterForSelf(record, key);
  return key;
}

async function wrapAndRegisterForSelf(record, dataKey) {
  const myPublicKey = await importPublicKey(record.public_key_b64);
  const wrapped = await wrapDataKey(dataKey, myPublicKey);
  await apiFetch("PATCH", `/api/devices/${record.device_id}/key/`, {
    encrypted_data_key: wrapped,
  });
}

async function distributeToPendingDevices(myDeviceId, dataKey) {
  const res = await apiFetch("GET", "/api/devices/");
  if (!res.ok) return;
  const { results: devices } = await res.json();

  for (const device of devices) {
    if (device.device_id === myDeviceId || device.has_data_key) continue;
    try {
      const recipientPublicKey = await importPublicKey(device.public_key);
      const wrapped = await wrapDataKey(dataKey, recipientPublicKey);
      await apiFetch("PATCH", `/api/devices/${device.device_id}/key/`, {
        encrypted_data_key: wrapped,
      });
    } catch (e) {
      console.warn(`[keystore] Could not distribute key to device ${device.device_id}:`, e);
    }
  }
}

async function loadOrCreateUserKeyPair(dataKey) {
  const res = await apiFetch("GET", "/api/userkeypair/");
  if (res.ok) {
    const { encrypted_private_key } = await res.json();
    return unwrapUserPrivateKey(encrypted_private_key, dataKey);
  }
  if (res.status !== 404) return null;

  const keyPair = await generateUserKeyPair();
  const publicKeyB64 = await exportUserPublicKey(keyPair.publicKey);
  const encryptedPrivateKey = await wrapUserPrivateKey(keyPair.privateKey, dataKey);

  const createRes = await apiFetch("POST", "/api/userkeypair/", {
    public_key: publicKeyB64,
    encrypted_private_key: encryptedPrivateKey,
  });
  if (!createRes.ok) return null;

  return unwrapUserPrivateKey(encryptedPrivateKey, dataKey);
}

async function doBootstrap() {
  let record = await getDeviceRecord();

  if (!record) {
    record = await registerDevice();
  }

  // Resolve data key
  if (record.data_key) {
    _dataKey = record.data_key;
  } else {
    const deviceRes = await apiFetch("GET", `/api/devices/${record.device_id}/`);
    if (!deviceRes.ok) throw new Error("Could not fetch device state from server");
    const deviceState = await deviceRes.json();

    _dataKey = await obtainDataKey(record, deviceState);

    if (_dataKey) {
      record = { ...record, data_key: _dataKey };
      await putDeviceRecord(record);
    }
  }

  // Migrate stored data key if it's missing wrapKey/unwrapKey usages.
  // Keys created before this fix only had ["encrypt","decrypt"], which causes
  // wrapUserPrivateKey to throw a DOMException.
  if (_dataKey && !_dataKey.usages.includes("wrapKey")) {
    try {
      const raw = await crypto.subtle.exportKey("raw", _dataKey);
      _dataKey = await crypto.subtle.importKey(
        "raw", raw, { name: "AES-GCM", length: 256 }, true,
        ["encrypt", "decrypt", "wrapKey", "unwrapKey"]
      );
      record = { ...record, data_key: _dataKey };
      await putDeviceRecord(record);
    } catch (e) {
      console.warn("[keystore] Could not migrate data key usages:", e);
    }
  }

  // Resolve user key pair (requires data key)
  if (_dataKey) {
    if (record.user_private_key) {
      _userPrivateKey = record.user_private_key;
    } else {
      _userPrivateKey = await loadOrCreateUserKeyPair(_dataKey);
      if (_userPrivateKey) {
        record = { ...record, user_private_key: _userPrivateKey };
        await putDeviceRecord(record);
      }
    }

    await distributeToPendingDevices(record.device_id, _dataKey);
  }
}

async function bootstrap() {
  try {
    await doBootstrap();
  } catch (e) {
    console.error("[keystore] Bootstrap failed:", e);
  } finally {
    _readyResolve(_dataKey);
  }
  if (_dataKey && !sessionStorage.getItem("ks:staged")) {
    sessionStorage.setItem("ks:staged", "1");
    runStaging().catch((e) => console.warn("[keystore] auto-staging failed:", e));
  }
}

window.keystore = {
  ready,
  getDataKey,
  getUserPrivateKey,
  encryptField,
  decryptField,
  encryptPayload,
  decryptPayload,
  decryptECIES,
  encryptFile,
  decryptFileBuffer,
  decryptMediaUrl,
  runStaging,
};

bootstrap();
