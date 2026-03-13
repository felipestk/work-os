function placeholderHtml() {
  return '<div class="detail-placeholder">Select a task to inspect its details.</div>';
}

function getDrawer() { return document.querySelector('[data-detail-drawer]'); }
function getBackdrop() { return document.querySelector('[data-detail-backdrop]'); }
function getPanel() { return document.querySelector('[data-detail-panel]'); }
function getProjectModal() { return document.querySelector('[data-project-modal]'); }
function getProjectModalBackdrop() { return document.querySelector('[data-project-modal-backdrop]'); }
function getProjectModalPanel() { return document.querySelector('[data-project-modal-panel]'); }

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

function openProjectModal() {
  const modal = getProjectModal();
  const backdrop = getProjectModalBackdrop();
  if (modal) {
    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
  }
  if (backdrop) backdrop.hidden = false;
}

function closeProjectModal(reset = true) {
  const modal = getProjectModal();
  const backdrop = getProjectModalBackdrop();
  const panel = getProjectModalPanel();
  if (modal) {
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
  }
  if (backdrop) backdrop.hidden = true;
  if (reset && panel) panel.innerHTML = '';
}

function clearResults(container) {
  if (container) container.innerHTML = '';
}

function closeAllPickers(except = null) {
  document.querySelectorAll('[data-project-picker-results], [data-customer-picker-results]').forEach((el) => {
    if (except && el === except) return;
    clearResults(el);
  });
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
  form.querySelectorAll('input[type="hidden"]').forEach((input) => { input.value = ''; });
  form.querySelectorAll('select').forEach((select) => { select.selectedIndex = 0; });
  if (window.htmx) window.htmx.trigger(form, 'submit');
}

async function fetchInto(url, resultsEl) {
  const response = await fetch(url, { headers: { 'X-Requested-With': 'fetch' } });
  if (!response.ok) return;
  resultsEl.innerHTML = await response.text();
}

function debounceSearch(input, callback) {
  const existing = input.dataset.searchTimer;
  if (existing) clearTimeout(Number(existing));
  const timer = setTimeout(callback, 180);
  input.dataset.searchTimer = String(timer);
}

function setActiveOption(results, index) {
  const options = Array.from(results.querySelectorAll('[data-project-select], [data-customer-select], [data-open-project-create], [data-apply-customer-query]'));
  options.forEach((option, i) => option.classList.toggle('is-active', i === index));
  results.dataset.activeIndex = String(index);
}

function moveActiveOption(input, direction) {
  const container = input.closest('[data-project-picker], [data-customer-picker]') || input.closest('form');
  const results = container?.querySelector('[data-project-picker-results], [data-customer-picker-results]');
  if (!results) return false;
  const options = Array.from(results.querySelectorAll('[data-project-select], [data-customer-select], [data-open-project-create], [data-apply-customer-query]'));
  if (!options.length) return false;
  const current = Number(results.dataset.activeIndex || -1);
  const next = current < 0 ? 0 : (current + direction + options.length) % options.length;
  setActiveOption(results, next);
  return true;
}

function activateCurrentOption(input) {
  const container = input.closest('[data-project-picker], [data-customer-picker]') || input.closest('form');
  const results = container?.querySelector('[data-project-picker-results], [data-customer-picker-results]');
  if (!results) return false;
  const index = Number(results.dataset.activeIndex || -1);
  const options = Array.from(results.querySelectorAll('[data-project-select], [data-customer-select], [data-open-project-create], [data-apply-customer-query]'));
  if (index < 0 || !options[index]) return false;
  options[index].click();
  return true;
}

function runProjectSearch(input) {
  const picker = input.closest('[data-project-picker]');
  const results = picker?.querySelector('[data-project-picker-results]');
  const searchUrl = input.dataset.searchUrl;
  if (!results || !searchUrl) return;
  const q = input.value || '';
  closeAllPickers(results);
  debounceSearch(input, async () => {
    await fetchInto(`${searchUrl}?q=${encodeURIComponent(q)}`, results);
    results.dataset.activeIndex = '-1';
  });
}

function runCustomerSearch(input) {
  const container = input.closest('[data-customer-picker]') || input.closest('form');
  const results = container?.querySelector('[data-customer-picker-results]');
  const searchUrl = input.dataset.searchUrl;
  if (!results || !searchUrl) return;
  const q = input.value || '';
  closeAllPickers(results);
  debounceSearch(input, async () => {
    await fetchInto(`${searchUrl}?q=${encodeURIComponent(q)}`, results);
    results.dataset.activeIndex = '-1';
  });
}

function autoSubmitFiltersFrom(element) {
  const form = element.closest('.filters-form');
  if (form && window.htmx) window.htmx.trigger(form, 'submit');
}

function applyProjectSelection(button) {
  const picker = button.closest('[data-project-picker]');
  if (!picker) return;
  const hidden = picker.querySelector('[data-project-picker-hidden]');
  const input = picker.querySelector('[data-project-picker-input]');
  const results = picker.querySelector('[data-project-picker-results]');
  if (hidden) hidden.value = button.dataset.projectId || '';
  if (input) input.value = button.dataset.projectLabel || '';
  clearResults(results);
  autoSubmitFiltersFrom(picker);
}

function applyCustomerSelection(button) {
  const container = button.closest('[data-customer-picker]') || button.closest('form');
  if (!container) return;
  const hidden = container.querySelector('[data-customer-picker-hidden]');
  const input = container.querySelector('[data-customer-picker-input], input[name="customer_name"]');
  const results = container.querySelector('[data-customer-picker-results]');
  if (hidden) hidden.value = button.dataset.customerName || '';
  if (input) input.value = button.dataset.customerName || '';
  clearResults(results);
  autoSubmitFiltersFrom(container);
}

function applyCustomerQuery(button) {
  const container = button.closest('[data-customer-picker]') || button.closest('form');
  if (!container) return;
  const hidden = container.querySelector('[data-customer-picker-hidden]');
  const input = container.querySelector('[data-customer-picker-input], input[name="customer_name"]');
  const results = container.querySelector('[data-customer-picker-results]');
  if (hidden) hidden.value = button.dataset.customerQuery || '';
  if (input) input.value = button.dataset.customerQuery || '';
  clearResults(results);
}

function openProjectCreateFromPicker(button) {
  const picker = button.closest('[data-project-picker]');
  if (!picker || !window.htmx) return;
  const origin = picker.dataset.origin || 'quick-add';
  const target = picker.dataset.target || 'project_id';
  const query = button.dataset.projectQuery || '';
  const panel = getProjectModalPanel();
  if (!panel) return;
  clearResults(picker.querySelector('[data-project-picker-results]'));
  window.htmx.ajax('GET', `/board/project-create?origin=${encodeURIComponent(origin)}&target=${encodeURIComponent(target)}`, { target: panel, swap: 'innerHTML' });
  openProjectModal();
  setTimeout(() => {
    const titleInput = panel.querySelector('input[name="project_title"]');
    if (titleInput && query) titleInput.value = query;
  }, 80);
}

function consumeCreatedProject(payload) {
  const origin = payload.dataset.origin;
  const targetName = payload.dataset.target;
  const projectId = payload.dataset.projectId;
  const projectLabel = payload.dataset.projectLabel;
  const scope = origin === 'detail-edit'
    ? document.querySelector('[data-detail-panel] .detail-edit-form')
    : document.querySelector('[data-quick-add-form="backlog"]');
  if (!scope) return closeProjectModal();
  const hidden = scope.querySelector(`input[name="${targetName}"]`);
  const picker = scope.querySelector('[data-project-picker]');
  if (hidden) hidden.value = projectId;
  if (picker) {
    const input = picker.querySelector('[data-project-picker-input]');
    const results = picker.querySelector('[data-project-picker-results]');
    if (input) input.value = projectLabel;
    clearResults(results);
  }
  closeProjectModal();
}

document.addEventListener('input', (event) => {
  const projectInput = event.target.closest('[data-project-picker-input]');
  if (projectInput) return runProjectSearch(projectInput);
  const customerInput = event.target.closest('[data-customer-picker-input]');
  if (customerInput) return runCustomerSearch(customerInput);
});

document.addEventListener('focusin', (event) => {
  const projectInput = event.target.closest('[data-project-picker-input]');
  if (projectInput) return runProjectSearch(projectInput);
  const customerInput = event.target.closest('[data-customer-picker-input]');
  if (customerInput) return runCustomerSearch(customerInput);
});

document.addEventListener('keydown', (event) => {
  const input = event.target.closest('[data-project-picker-input], [data-customer-picker-input]');
  if (input) {
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      moveActiveOption(input, 1);
      return;
    }
    if (event.key === 'ArrowUp') {
      event.preventDefault();
      moveActiveOption(input, -1);
      return;
    }
    if (event.key === 'Enter') {
      if (activateCurrentOption(input)) {
        event.preventDefault();
        return;
      }
    }
  }

  if (event.key === 'Escape') {
    closeDrawer(false);
    closeProjectModal(false);
    closeAllPickers();
  }
});

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

  const projectSelect = event.target.closest('[data-project-select]');
  if (projectSelect) return applyProjectSelection(projectSelect);

  const openProjectCreate = event.target.closest('[data-open-project-create]');
  if (openProjectCreate) return openProjectCreateFromPicker(openProjectCreate);

  const customerSelect = event.target.closest('[data-customer-select]');
  if (customerSelect) return applyCustomerSelection(customerSelect);

  const customerQuery = event.target.closest('[data-apply-customer-query]');
  if (customerQuery) return applyCustomerQuery(customerQuery);

  const modalClose = event.target.closest('[data-project-modal-close]');
  if (modalClose) return closeProjectModal();

  const modalBackdrop = event.target.closest('[data-project-modal-backdrop]');
  if (modalBackdrop) return closeProjectModal();

  const insidePicker = event.target.closest('[data-project-picker], [data-customer-picker], [data-project-modal]');
  if (!insidePicker) closeAllPickers();
});

document.body.addEventListener('htmx:afterSwap', (event) => {
  const target = event.detail.target;
  if (target && target.matches && target.matches('[data-detail-panel]')) openDrawer();
  if (target && target.id === 'board-shell') closeDrawer(false);
  if (target && target.matches && target.matches('[data-project-modal-panel]')) {
    openProjectModal();
    const payload = target.querySelector('[data-created-project]');
    if (payload) consumeCreatedProject(payload);
  }
});
