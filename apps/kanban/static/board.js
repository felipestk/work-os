function placeholderHtml() {
  return '<div class="detail-placeholder">Select a task to inspect its details.</div>';
}

function getDrawer() { return document.querySelector('[data-detail-drawer]'); }
function getBackdrop() { return document.querySelector('[data-detail-backdrop]'); }
function getPanel() { return document.querySelector('[data-detail-panel]'); }

function openDrawer() {
  const drawer = getDrawer();
  const backdrop = getBackdrop();
  if (drawer) {
    drawer.classList.add('is-open');
    drawer.setAttribute('aria-hidden', 'false');
  }
  if (backdrop) {
    backdrop.hidden = false;
    backdrop.classList.add('is-open');
  }
}

function closeDrawer(resetPanel = false) {
  const drawer = getDrawer();
  const backdrop = getBackdrop();
  const panel = getPanel();
  if (drawer) {
    drawer.classList.remove('is-open');
    drawer.setAttribute('aria-hidden', 'true');
  }
  if (backdrop) {
    backdrop.classList.remove('is-open');
    backdrop.hidden = true;
  }
  if (resetPanel && panel) panel.innerHTML = placeholderHtml();
}

function toggleQuickAdd(columnKey, open) {
  const form = document.querySelector(`[data-quick-add-form="${columnKey}"]`);
  const button = document.querySelector(`[data-quick-add-toggle="${columnKey}"]`);
  if (!form || !button) return;
  const shouldOpen = open ?? form.hidden;
  form.hidden = !shouldOpen;
  button.hidden = shouldOpen;
  if (shouldOpen) {
    const firstInput = form.querySelector('input[name="title"]');
    if (firstInput) firstInput.focus();
  }
}

function resetFilters() {
  const form = document.querySelector('.filters-form');
  if (!form) return;
  form.querySelectorAll('input[type="text"]').forEach((input) => { input.value = ''; });
  form.querySelectorAll('select').forEach((select) => { select.selectedIndex = 0; });
  if (window.htmx) window.htmx.trigger(form, 'submit');
}

function toggleInlineCreate(button) {
  const form = button.closest('form');
  if (!form) return;
  const fields = form.querySelector('[data-inline-create-fields]');
  if (!fields) return;
  const isHidden = fields.hidden;
  fields.hidden = !isHidden;
  button.classList.toggle('is-active', isHidden);
  button.textContent = isHidden ? '− Use existing project instead' : '+ Or create customer + project';
}

document.addEventListener('click', (event) => {
  const close = event.target.closest('[data-detail-close]');
  if (close) return closeDrawer(true);

  const backdrop = event.target.closest('[data-detail-backdrop]');
  if (backdrop) return closeDrawer(false);

  const quickAddToggle = event.target.closest('[data-quick-add-toggle]');
  if (quickAddToggle) return toggleQuickAdd(quickAddToggle.dataset.quickAddToggle, true);

  const quickAddClose = event.target.closest('[data-quick-add-close]');
  if (quickAddClose) return toggleQuickAdd(quickAddClose.dataset.quickAddClose, false);

  const resetFiltersButton = event.target.closest('[data-reset-filters]');
  if (resetFiltersButton) return resetFilters();

  const inlineCreateToggle = event.target.closest('[data-inline-create-toggle]');
  if (inlineCreateToggle) return toggleInlineCreate(inlineCreateToggle);
});

document.body.addEventListener('htmx:afterSwap', (event) => {
  const target = event.detail.target;
  if (target && target.matches && target.matches('[data-detail-panel]')) openDrawer();
  if (target && target.id === 'board-shell') closeDrawer(false);
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') closeDrawer(false);
});
