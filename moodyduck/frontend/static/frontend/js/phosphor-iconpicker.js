const PHOSPHOR_ICONS = [
  // Symbols & UI
  'ph-arrow-right', 'ph-arrow-left', 'ph-arrow-up', 'ph-arrow-down',
  'ph-caret-right', 'ph-caret-left', 'ph-caret-up', 'ph-caret-down',
  'ph-check', 'ph-check-circle', 'ph-x', 'ph-x-circle',
  'ph-plus', 'ph-plus-circle', 'ph-minus', 'ph-minus-circle',
  'ph-info', 'ph-warning', 'ph-warning-circle', 'ph-question',

  // Objects
  'ph-star', 'ph-heart', 'ph-bookmark', 'ph-flag', 'ph-tag', 'ph-bell',
  'ph-calendar', 'ph-clock', 'ph-alarm', 'ph-timer',
  'ph-book', 'ph-book-open', 'ph-notebook', 'ph-notepad',
  'ph-pencil', 'ph-pencil-simple', 'ph-pen', 'ph-eraser',
  'ph-trash', 'ph-archive', 'ph-floppy-disk', 'ph-paperclip', 'ph-link',
  'ph-lock', 'ph-lock-simple', 'ph-lock-open', 'ph-key',
  'ph-gear', 'ph-sliders-horizontal', 'ph-funnel', 'ph-sort-ascending',

  // People & user
  'ph-user', 'ph-user-circle', 'ph-user-gear', 'ph-user-plus', 'ph-users',
  'ph-sign-in', 'ph-sign-out', 'ph-house', 'ph-buildings',

  // Nature & environment
  'ph-leaf', 'ph-tree', 'ph-plant', 'ph-flower', 'ph-drop', 'ph-fire',
  'ph-cloud', 'ph-cloud-fog', 'ph-cloud-rain', 'ph-cloud-snow',
  'ph-sun', 'ph-moon', 'ph-wind', 'ph-snowflake',

  // Health & wellness
  'ph-heartbeat', 'ph-first-aid', 'ph-pill', 'ph-syringe',
  'ph-bandaids', 'ph-thermometer', 'ph-brain', 'ph-eye', 'ph-tooth',

  // Food & lifestyle
  'ph-coffee', 'ph-fork-knife', 'ph-cake', 'ph-beer-stein',
  'ph-wine', 'ph-pizza', 'ph-hamburger',

  // Activities
  'ph-bicycle', 'ph-car', 'ph-airplane', 'ph-boat',
  'ph-football', 'ph-basketball', 'ph-barbell', 'ph-person-simple-run',
  'ph-swimming-pool', 'ph-tennis-ball',

  // Tech & media
  'ph-camera', 'ph-music-note', 'ph-music-notes', 'ph-headphones',
  'ph-film-strip', 'ph-television', 'ph-monitor',
  'ph-phone', 'ph-chat', 'ph-envelope', 'ph-globe',
  'ph-wifi', 'ph-bluetooth', 'ph-battery-full',

  // Misc
  'ph-feather', 'ph-scales', 'ph-chart-pie', 'ph-chart-bar',
  'ph-list', 'ph-list-bullets', 'ph-grid-four', 'ph-table',
  'ph-map', 'ph-map-pin', 'ph-compass',
  'ph-smiley', 'ph-smiley-sad', 'ph-smiley-nervous', 'ph-smiley-wink',
  'ph-bed', 'ph-moon-stars', 'ph-sparkle', 'ph-magic-wand',
  'ph-lightning', 'ph-hand-heart', 'ph-hands-praying',
];

document.addEventListener('DOMContentLoaded', function() {
  const modalId = 'phosphorIconPickerModal';
  if (!document.getElementById(modalId)) {
    document.body.insertAdjacentHTML('beforeend', `
      <div class="modal fade" id="${modalId}" tabindex="-1">
        <div class="modal-dialog modal-lg">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Choose Icon</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
              <input type="search" id="iconPickerSearch" class="form-control mb-3" placeholder="Search icons...">
              <div id="iconPickerGrid" class="icon-picker-grid"></div>
            </div>
          </div>
        </div>
      </div>
    `);
  }

  let activeInput = null;

  document.querySelectorAll('input.phosphor-icon-picker').forEach(input => {
    const wrapper = document.createElement('div');
    wrapper.className = 'phosphor-icon-picker-wrapper';
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);
    input.type = 'hidden';

    const preview = document.createElement('div');
    preview.className = 'icon-picker-preview d-flex align-items-center gap-2 p-2 border rounded';

    const iconEl = document.createElement('i');
    iconEl.className = (input.value || 'ph ph-star') + ' icon-picker-icon-preview fs-4';

    const valueSpan = document.createElement('span');
    valueSpan.className = 'text-muted small flex-grow-1';
    valueSpan.textContent = input.value || 'ph ph-star';

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'btn btn-sm btn-outline-secondary';
    btn.innerHTML = '<i class="ph ph-magnifying-glass me-1"></i> Browse';

    preview.appendChild(iconEl);
    preview.appendChild(valueSpan);
    preview.appendChild(btn);
    wrapper.appendChild(preview);

    btn.addEventListener('click', () => {
      activeInput = input;
      populateGrid(input.value);
      const modal = new bootstrap.Modal(document.getElementById(modalId));
      modal.show();
    });
  });

  document.getElementById('iconPickerSearch')?.addEventListener('input', function() {
    const q = this.value.toLowerCase();
    document.querySelectorAll('#iconPickerGrid .icon-option').forEach(el => {
      el.style.display = el.dataset.name.includes(q) ? '' : 'none';
    });
  });

  function populateGrid(currentValue) {
    const grid = document.getElementById('iconPickerGrid');
    document.getElementById('iconPickerSearch').value = '';
    grid.innerHTML = '';
    PHOSPHOR_ICONS.forEach(iconName => {
      const fullClass = 'ph ' + iconName;
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'icon-option btn ' + (fullClass === currentValue ? 'btn-primary' : 'btn-outline-secondary');
      btn.dataset.name = iconName.replace('ph-', '');
      btn.dataset.value = fullClass;
      btn.title = iconName.replace('ph-', '').replace(/-/g, ' ');
      btn.innerHTML = `<i class="${fullClass}"></i>`;
      btn.addEventListener('click', () => selectIcon(fullClass));
      grid.appendChild(btn);
    });
  }

  function selectIcon(fullClass) {
    if (!activeInput) return;
    activeInput.value = fullClass;
    const wrapper = activeInput.parentElement;
    wrapper.querySelector('.icon-picker-icon-preview').className = fullClass + ' icon-picker-icon-preview fs-4';
    wrapper.querySelector('.text-muted').textContent = fullClass;
    bootstrap.Modal.getInstance(document.getElementById('phosphorIconPickerModal')).hide();
  }
});
