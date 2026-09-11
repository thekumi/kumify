// Intercepts HTML form submissions and populates a hidden "encrypted_payload"
// input for any form marked with data-keystore-encrypt.
//
// Two ways to mark text fields for encryption:
//
//  1. Per-input attribute (explicit forms):
//       <input name="title" data-encrypt-field>
//       <textarea name="text" data-encrypt-field="text"></textarea>
//     The optional attribute value overrides the key used in the payload.
//
//  2. Form-level list (generic-rendered forms):
//       <form data-keystore-encrypt data-encrypt-fields="name,remarks">
//     Comma-separated field names; the script finds inputs by name.
//
// To encrypt file uploads, add data-encrypt-files to the file input:
//       <input type="file" name="uploads" data-encrypt-files>
// Each file is AES-GCM encrypted before upload. Metadata (filename, mime_type)
// is encrypted and sent as a JSON array in "encrypted_file_metadata".

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("form[data-keystore-encrypt]").forEach((form) => {
    form.addEventListener("submit", async (e) => {
      if (!window.keystore) return;
      const dataKey = await window.keystore.ready;
      if (!dataKey) return;

      const fields = {};

      // Approach 1: explicit data-encrypt-field attributes on inputs
      form.querySelectorAll("[data-encrypt-field]").forEach((el) => {
        const fieldName = el.dataset.encryptField || el.name;
        const value = el.value;
        if (fieldName && value) fields[fieldName] = value;
      });

      // Approach 2: form-level data-encrypt-fields="name,remarks,..."
      const fieldList = (form.dataset.encryptFields || "")
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      for (const name of fieldList) {
        if (fields[name] !== undefined) continue;
        const el = form.querySelector(`[name="${CSS.escape(name)}"]`);
        if (el && el.value) fields[name] = el.value;
      }

      const fileInput = form.querySelector('input[type="file"][data-encrypt-files]');
      const hasFiles = fileInput && fileInput.files.length > 0;
      const hasTextFields = Object.keys(fields).length > 0;

      if (!hasTextFields && !hasFiles) return;

      e.preventDefault();

      if (hasTextFields) {
        const payload = await window.keystore.encryptPayload(dataKey, fields);
        let hiddenInput = form.querySelector('input[name="encrypted_payload"]');
        if (!hiddenInput) {
          hiddenInput = document.createElement("input");
          hiddenInput.type = "hidden";
          hiddenInput.name = "encrypted_payload";
          form.appendChild(hiddenInput);
        }
        hiddenInput.value = JSON.stringify(payload);
      }

      if (hasFiles) {
        const dt = new DataTransfer();
        const encMeta = [];
        for (const file of fileInput.files) {
          const encBlob = await window.keystore.encryptFile(dataKey, file);
          dt.items.add(new File([encBlob], file.name + ".enc", { type: "application/octet-stream" }));
          const metaPayload = await window.keystore.encryptPayload(dataKey, {
            filename: file.name,
            mime_type: file.type || "application/octet-stream",
          });
          encMeta.push(metaPayload);
        }
        fileInput.files = dt.files;

        let metaInput = form.querySelector('input[name="encrypted_file_metadata"]');
        if (!metaInput) {
          metaInput = document.createElement("input");
          metaInput.type = "hidden";
          metaInput.name = "encrypted_file_metadata";
          form.appendChild(metaInput);
        }
        metaInput.value = JSON.stringify(encMeta);
      }

      form.submit();
    });
  });
});
