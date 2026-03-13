document.addEventListener('click', (event) => {
  const toggle = event.target.closest('[data-detail-close]');
  if (!toggle) return;
  const panel = document.querySelector('[data-detail-panel]');
  if (panel) panel.innerHTML = '<div class="detail-placeholder">Select a task to inspect its details.</div>';
});
