// Shows a Bootstrap 5 modal prompting for the recovery passphrase.
// onAttempt(passphrase) should return the data key on success or throw on failure.
// Resolves with the data key once unlocked.
export function promptPassphrase(onAttempt) {
  return new Promise((resolve) => {
    document.body.insertAdjacentHTML(
      "beforeend",
      `<div class="modal fade" id="ks-passphrase-modal" tabindex="-1"
            data-bs-backdrop="static" data-bs-keyboard="false" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header border-0 pb-0">
              <h5 class="modal-title">Unlock your data</h5>
            </div>
            <div class="modal-body">
              <p class="text-muted small mb-3">
                Enter your recovery passphrase to access your encrypted data on this device.
              </p>
              <div id="ks-passphrase-error" class="alert alert-danger d-none small py-2"></div>
              <input type="password" id="ks-passphrase-input" class="form-control"
                     placeholder="Recovery passphrase" autocomplete="current-password">
            </div>
            <div class="modal-footer border-0 pt-0">
              <button id="ks-passphrase-btn" class="btn btn-primary w-100">Unlock</button>
            </div>
          </div>
        </div>
      </div>`
    );

    const el = document.getElementById("ks-passphrase-modal");
    const modal = new bootstrap.Modal(el);
    const input = document.getElementById("ks-passphrase-input");
    const btn = document.getElementById("ks-passphrase-btn");
    const errorEl = document.getElementById("ks-passphrase-error");

    modal.show();
    el.addEventListener("shown.bs.modal", () => input.focus());

    async function attempt() {
      const passphrase = input.value;
      if (!passphrase) return;
      btn.disabled = true;
      btn.textContent = "Unlocking…";
      errorEl.classList.add("d-none");
      try {
        const key = await onAttempt(passphrase);
        modal.hide();
        el.remove();
        resolve(key);
      } catch {
        errorEl.textContent = "Incorrect passphrase. Please try again.";
        errorEl.classList.remove("d-none");
        btn.disabled = false;
        btn.textContent = "Unlock";
        input.value = "";
        input.focus();
      }
    }

    btn.addEventListener("click", attempt);
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") attempt();
    });
  });
}

// Shows a dismissible banner when this device is awaiting key distribution
// from another already-authorised device.
export function showWaitingBanner() {
  if (document.getElementById("ks-waiting-banner")) return;
  document.body.insertAdjacentHTML(
    "afterbegin",
    `<div id="ks-waiting-banner" class="alert alert-info m-0 rounded-0 text-center small py-2">
      <strong>Waiting for authorisation.</strong>
      Log in on a paired device to grant this device access to your encrypted data.
    </div>`
  );
}
