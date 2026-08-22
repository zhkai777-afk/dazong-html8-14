(() => {
  let dirty = false;
  let pendingAction = null;

  const $ = (selector) => document.querySelector(selector);
  const status = $("#saveState");
  const saveButtons = () => [...document.querySelectorAll("[data-save-data]")];
  const timeText = () => new Intl.DateTimeFormat("zh-CN", { hour: "2-digit", minute: "2-digit", second: "2-digit" }).format(new Date());

  function updateButtons() {
    saveButtons().forEach((button) => {
      button.classList.toggle("primary", dirty);
      button.disabled = !dirty;
      button.setAttribute("aria-disabled", String(!dirty));
      button.title = dirty ? "有未保存的数据" : "当前没有需要保存的修改";
    });
  }

  function updateStatus(message) {
    if (status) status.textContent = message;
  }

  function markDirty() {
    if (dirty) return;
    dirty = true;
    updateStatus("数据已修改，尚未保存");
    updateButtons();
  }

  function saveData() {
    dirty = false;
    updateButtons();
    updateStatus(`最近保存：${timeText()}`);
  }

  const dialog = document.createElement("dialog");
  dialog.className = "unsaved-data-dialog";
  dialog.innerHTML = `<div class="unsaved-dialog-head"><h3>存在未保存的数据</h3></div><div class="unsaved-dialog-body"><p>当前修改尚未保存。继续切换页签或离开页面可能导致数据丢失和计算结果偏差。</p></div><footer><button type="button" class="button secondary" data-unsaved-cancel>取消并跳转</button><button type="button" class="button primary" data-unsaved-save>保存数据</button></footer>`;
  document.body.append(dialog);

  const style = document.createElement("style");
  style.textContent = `.unsaved-data-dialog{width:min(460px,calc(100vw - 32px));border:0;border-radius:10px;padding:0;color:var(--text,#15202f);box-shadow:0 20px 60px rgba(18,37,60,.3)}.unsaved-data-dialog::backdrop{background:rgba(17,31,48,.38)}.unsaved-dialog-head{padding:16px 18px;border-bottom:1px solid var(--border,#d7dee7);background:var(--primary-soft,#edf3f8)}.unsaved-dialog-head h3,.unsaved-dialog-body p{margin:0}.unsaved-dialog-head h3{font-size:16px}.unsaved-dialog-body{padding:18px}.unsaved-dialog-body p{color:var(--text-secondary,#526071);font-size:13px;line-height:1.65}.unsaved-data-dialog footer{display:flex;justify-content:flex-end;gap:8px;padding:14px 18px;border-top:1px solid var(--border,#d7dee7)}.workspace-footer:has([data-save-data]){justify-content:flex-end}`;
  document.head.append(style);

  function runPendingAction() {
    const action = pendingAction;
    pendingAction = null;
    if (typeof action === "function") action();
  }

  function promptBeforeLeaving(action) {
    if (!dirty) { action(); return; }
    pendingAction = action;
    if (!dialog.open) dialog.showModal();
  }

  dialog.addEventListener("click", (event) => {
    if (event.target.closest("[data-unsaved-save]")) {
      saveData();
      dialog.close();
      runPendingAction();
    }
    if (event.target.closest("[data-unsaved-cancel]")) {
      dirty = false;
      updateButtons();
      updateStatus("数据未保存，已跳转至目标页面");
      dialog.close();
      runPendingAction();
    }
  });

  document.addEventListener("input", (event) => {
    if (event.target.matches("input, textarea, select")) markDirty();
  }, true);
  document.addEventListener("change", (event) => {
    if (event.target.matches("input, textarea, select")) markDirty();
  }, true);
  document.addEventListener("click", (event) => {
    const save = event.target.closest("[data-save-data], #saveDraftBtn");
    if (save) {
      event.preventDefault();
      event.stopImmediatePropagation();
      saveData();
      return;
    }
    const link = event.target.closest("a[href]");
    if (link && !link.target && link.getAttribute("href") && !link.getAttribute("href").startsWith("#")) {
      event.preventDefault();
      event.stopImmediatePropagation();
      promptBeforeLeaving(() => { window.location.href = link.href; });
      return;
    }
    const tab = event.target.closest('[role="tab"]');
    if (tab && dirty) {
      event.preventDefault();
      event.stopImmediatePropagation();
      promptBeforeLeaving(() => tab.click());
      return;
    }
    const action = event.target.closest("button");
    if (action && /添加|删除|移除/.test(action.textContent || "")) markDirty();
  }, true);
  window.addEventListener("beforeunload", (event) => {
    if (!dirty) return;
    event.preventDefault();
    event.returnValue = "";
  });

  saveButtons().forEach((button) => button.addEventListener("click", saveData));
  updateStatus("最近保存：未保存");
  updateButtons();
})();
