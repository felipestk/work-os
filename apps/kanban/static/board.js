function placeholderHtml() {
  return '<div class="detail-placeholder">Select a task to inspect its details.</div>';
}

function getDrawer() {
  return document.querySelector('[data-detail-drawer]');
}

function getBackdrop() {
  return document.querySelector('[data-detail-backdrop]');
}

function getPanel() {
  return document.querySelector('[data-detail-panel]');
}

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

document.addEventListener('click', (event) => {
  const close = event.target.closest('[data-detail-close]');
  if (close) {
    closeDrawer(true);
    return;
  }

  const backdrop = event.target.closest('[data-detail-backdrop]');
  if (backdrop) {
    closeDrawer(false);
    return;
  }

  const quickAddToggle = event.target.closest('[data-quick-add-toggle]');
  if (quickAddToggle) {
    toggleQuickAdd(quickAddToggle.dataset.quickAddToggle, true);
    return;
  }

  const quickAddClose = event.target.closest('[data-quick-add-close]');
  if (quickAddClose) {
    toggleQuickAdd(quickAddClose.dataset.quickAddClose, false);
  }
});

document.body.addEventListener('htmx:afterSwap', (event) => {
  const target = event.detail.target;
  if (target && target.matches && target.matches('[data-detail-panel]')) {
    openDrawer();
  }
  if (target && target.id === 'board-columns') {
    closeDrawer(false);
  }
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') closeDrawer(false);
});
