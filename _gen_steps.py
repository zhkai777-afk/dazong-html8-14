# -*- coding: utf-8 -*-
"""批量生成卸货检验作业台 8 步录入页（除已确认的 step-02 外，生成 01/03/04/05/06/07/08）。
输出为单文件、无外部依赖的 HTML，样式沿用 prototype/app/globals.css，交互内置与原件一致的计算逻辑。"""
import os

CSS = r"""
    :root {
      --primary: #1e3a5f; --primary-strong: #142b46; --primary-soft: #eaf0f7;
      --accent: #047857; --accent-soft: #e7f5ef; --warning: #a16207; --warning-soft: #fff7d6;
      --danger: #b42318; --danger-soft: #fff0ee; --background: #eef2f6; --surface: #ffffff;
      --surface-muted: #f7f9fb; --text: #15202f; --text-secondary: #526071; --border: #d7dee7;
      --border-strong: #b8c3d0; --focus: #2563eb; --sidebar: #152438; --sidebar-muted: #9eacbd; --radius: 6px;
    }
    * { box-sizing: border-box; }
    html { background: var(--background); }
    body { margin: 0; background: var(--background); color: var(--text); font-family: "Segoe UI", "Microsoft YaHei UI", "PingFang SC", Arial, sans-serif; font-size: 14px; line-height: 1.5; }
    button, input, select { font: inherit; }
    button { cursor: pointer; }
    button:disabled { cursor: not-allowed; opacity: .48; }
    button:focus-visible, input:focus-visible, select:focus-visible, a:focus-visible { outline: 3px solid color-mix(in srgb, var(--focus) 35%, transparent); outline-offset: 2px; }

    .skip-link { position: fixed; z-index: 1000; top: -60px; left: 16px; padding: 10px 14px; background: white; color: var(--text); border: 1px solid var(--border); }
    .skip-link:focus { top: 12px; }

    .app-shell { min-height: 100vh; display: grid; grid-template-columns: 196px minmax(0, 1fr); }
    .global-sidebar { position: sticky; top: 0; height: 100vh; padding: 20px 14px; background: var(--sidebar); color: white; display: flex; flex-direction: column; }
    .product-mark { display: flex; align-items: center; gap: 10px; padding: 0 6px 22px; border-bottom: 1px solid rgba(255,255,255,.12); }
    .mark-square { width: 38px; height: 38px; display: grid; place-items: center; border: 1px solid rgba(255,255,255,.55); border-radius: 5px; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-weight: 700; letter-spacing: .04em; }
    .product-mark strong, .product-mark small { display: block; }
    .product-mark strong { font-size: 15px; }
    .product-mark small { color: var(--sidebar-muted); font-size: 11px; }
    .global-nav { display: grid; gap: 6px; margin-top: 20px; }
    .global-nav button { min-height: 46px; padding: 0 10px; display: flex; align-items: center; justify-content: space-between; border: 1px solid transparent; border-radius: 5px; background: transparent; color: #d8e0ea; text-align: left; transition: background 180ms ease, border-color 180ms ease; }
    .global-nav button:hover { background: rgba(255,255,255,.07); }
    .global-nav button.selected { background: #243951; border-color: #405873; color: white; }
    .global-nav span > small { display: block; color: var(--sidebar-muted); font-size: 8px; font-weight: 500; letter-spacing: .02em; }
    .global-nav em { color: var(--sidebar-muted); font-size: 10px; font-style: normal; }
    .offline-card { margin-top: auto; padding: 12px 10px; border: 1px solid rgba(255,255,255,.13); border-radius: 5px; display: flex; gap: 9px; align-items: center; background: rgba(255,255,255,.04); }
    .offline-card strong, .offline-card small { display: block; }
    .offline-card strong { font-size: 12px; }
    .offline-card small { font-size: 10px; color: var(--sidebar-muted); }
    .status-dot { width: 8px; height: 8px; border-radius: 50%; background: #34d399; box-shadow: 0 0 0 3px rgba(52,211,153,.15); }

    .main-stage { min-width: 0; }
    .topbar { min-height: 78px; padding: 13px 24px; display: flex; align-items: center; justify-content: space-between; gap: 24px; background: var(--surface); border-bottom: 1px solid var(--border); }
    .breadcrumb { color: var(--text-secondary); font-size: 11px; }
    .topbar h1 { margin: 2px 0 0; font-size: 20px; line-height: 1.25; letter-spacing: -.01em; }
    .topbar-meta { display: flex; align-items: center; gap: 10px; }
    .project-state { padding: 5px 9px; border: 1px solid #8cc9b5; border-radius: 999px; color: #09614b; background: var(--accent-soft); font-size: 11px; font-weight: 650; }
    .save-state { color: var(--text-secondary); font-size: 11px; min-width: 130px; text-align: right; }
    .button { min-height: 38px; padding: 0 14px; border-radius: 5px; border: 1px solid transparent; font-weight: 650; transition: background 160ms ease, border-color 160ms ease; }
    .button.primary { background: var(--primary); color: white; }
    .button.primary:hover:not(:disabled) { background: var(--primary-strong); }
    .button.secondary { background: white; border-color: var(--border-strong); color: var(--text); }
    .button.secondary:hover:not(:disabled), .button.tertiary:hover:not(:disabled) { border-color: #8494a8; background: var(--surface-muted); }
    .button.tertiary { background: transparent; color: var(--primary); border-color: var(--border); }

    .project-strip { min-height: 58px; padding: 8px 24px; display: grid; grid-template-columns: 1.3fr 1.5fr 1.2fr 1.2fr; gap: 8px; background: #f8fafc; border-bottom: 1px solid var(--border); }
    .project-strip dl { margin: 0; padding: 2px 16px 2px 0; border-right: 1px solid var(--border); }
    .project-strip dl:last-child { border-right: 0; }
    .project-strip dt { color: var(--text-secondary); font-size: 10px; }
    .project-strip dt small { margin-left: 4px; color: #7a8796; font-size: 9px; font-weight: 500; }
    .project-strip dd { margin: 1px 0 0; font-size: 12px; font-weight: 650; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

    .workbench-grid { min-height: calc(100vh - 137px); display: grid; grid-template-columns: 238px minmax(0, 1fr); }
    .workflow-panel { padding: 17px 13px; background: #f7f9fb; border-right: 1px solid var(--border); }
    .panel-heading { padding: 0 6px; display: flex; align-items: end; justify-content: space-between; }
    .eyebrow { margin: 0 0 2px; color: var(--text-secondary); font-size: 10px; font-weight: 700; letter-spacing: .09em; text-transform: uppercase; }
    .panel-heading h2 { margin: 0; font-size: 17px; }
    .panel-heading h2 small { margin-left: 6px; color: var(--text-secondary); font-size: 11px; font-weight: 550; }
    .panel-heading > strong { color: var(--accent); font: 700 16px/1 ui-monospace, Consolas, monospace; }
    .progress-track { height: 4px; margin: 11px 6px 16px; overflow: hidden; border-radius: 99px; background: #dce3eb; }
    .progress-track span { display: block; height: 100%; background: var(--accent); }
    .workflow-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 3px; }
    .workflow-list a, .workflow-list button { width: 100%; min-height: 50px; padding: 6px 7px; border: 1px solid transparent; border-radius: 5px; background: transparent; display: grid; grid-template-columns: 28px 1fr 10px; gap: 8px; align-items: center; text-align: left; color: inherit; text-decoration: none; }
    .workflow-list a:hover, .workflow-list button:hover { background: white; border-color: var(--border); }
    .workflow-list .active a, .workflow-list .active button { background: white; border-color: #8ca6c3; box-shadow: inset 3px 0 var(--primary); }
    .step-index { color: #7c8999; font: 650 11px/1 ui-monospace, Consolas, monospace; }
    .step-copy strong, .step-copy em, .step-copy small { display: block; }
    .step-copy strong { font-size: 12px; }
    .step-copy em { margin-top: -1px; overflow: hidden; color: #667586; font-size: 8px; font-style: normal; line-height: 1.25; text-overflow: ellipsis; white-space: nowrap; }
    .step-copy small { margin-top: 1px; color: var(--text-secondary); font-size: 10px; }
    .step-state { width: 8px; height: 8px; border: 1px solid #aab5c1; border-radius: 50%; }
    .done .step-state { border-color: var(--accent); background: var(--accent); box-shadow: inset 0 0 0 2px white; }
    .partial .step-state { border-color: #4f78a5; background: linear-gradient(90deg, #4f78a5 50%, white 50%); }
    .warning .step-state { border-color: var(--warning); background: var(--warning-soft); }
    .active .step-state { border-color: var(--primary); background: var(--primary); }

    .workspace { min-width: 0; padding: 18px 22px 22px; }
    .workspace-heading { display: flex; justify-content: space-between; gap: 22px; align-items: flex-end; }
    .workspace-heading h2 { font-size: 19px; margin: 0; }
    .workspace-heading p:not(.eyebrow) { max-width: 720px; margin: 4px 0 0; color: var(--text-secondary); font-size: 12px; }
    .workspace-heading h2 small { font-size: 12px; font-weight: 500; color: var(--text-secondary); }
    .context-actions { display: flex; gap: 7px; align-items: flex-end; }
    .workspace-footer { margin-top: 14px; padding-top: 14px; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border); }
    .workspace-footer strong, .workspace-footer span { display: block; }
    .workspace-footer strong { font-size: 12px; }
    .workspace-footer span { margin-top: 2px; color: var(--text-secondary); font-size: 10px; }
    .workspace-footer a.button { display: inline-flex; align-items: center; text-decoration: none; }

    .metric-row { margin-top: 15px; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); border: 1px solid var(--border); border-radius: var(--radius); background: var(--surface); overflow: hidden; }
    .metric-row article { min-height: 87px; padding: 13px 15px; border-right: 1px solid var(--border); }
    .metric-row article:last-child { border-right: 0; }
    .metric-row span, .metric-row small, .metric-row strong { display: block; }
    .metric-row span { color: var(--text-secondary); font-size: 10px; }
    .metric-row strong { margin: 5px 0 2px; font: 700 20px/1.15 ui-monospace, Consolas, monospace; font-variant-numeric: tabular-nums; }
    .metric-row small { color: var(--text-secondary); font-size: 10px; }
    .metric-row .metric-accent { background: var(--accent-soft); }
    .metric-row .metric-accent strong { color: #075d49; }
    .metric-row .metric-warning { background: var(--warning-soft); }
    .metric-row .metric-warning strong { color: #744602; }

    .table-card { margin-top: 12px; border: 1px solid var(--border); border-radius: var(--radius); background: white; overflow: hidden; }
    .table-scroll { overflow-x: auto; }
    table { width: 100%; min-width: 1000px; border-collapse: collapse; font-size: 11px; }
    th, td { height: 41px; padding: 5px 8px; border-right: 1px solid #e5e9ef; border-bottom: 1px solid #e5e9ef; text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; }
    thead th { height: 36px; background: #f3f6f9; color: #4b5868; font-size: 10px; font-weight: 700; }
    tbody th, thead th:first-child, td.text-left, th.text-left { text-align: left; }
    tbody tr:hover { background: #f8fbff; }
    tbody input { height: 28px; padding: 0 6px; border: 1px solid transparent; border-radius: 3px; background: #f8fbff; color: var(--text); text-align: right; font-variant-numeric: tabular-nums; }
    tbody input:hover, tbody input:focus { border-color: #8ba6c4; background: white; }
    tbody select { height: 28px; padding: 0 6px; border: 1px solid var(--border); border-radius: 3px; background: white; color: var(--text); }
    .calculated { background: #f3f6f9; font-weight: 650; }
    .calculated.strong { color: var(--primary-strong); }
    .number { text-align: right; font-variant-numeric: tabular-nums; }

    .status-pill { display: inline-block; min-width: 48px; padding: 3px 6px; border-radius: 999px; text-align: center; font-size: 9px; font-weight: 700; }
    .status-pill.success { color: #075d49; background: var(--accent-soft); }
    .status-pill.warning { color: #744602; background: var(--warning-soft); }
    .status-pill.danger { color: var(--danger); background: var(--danger-soft); }
    .status-pill.neutral { color: #586474; background: #eef1f4; }
    .source-badge { display: inline-block; flex: none; padding: 2px 6px; border: 1px solid; border-radius: 999px; font-size: 9px; font-style: normal; font-weight: 700; white-space: nowrap; }
    .source-badge.project { color: #075d49; border-color: #8cc9b5; background: var(--accent-soft); }
    .source-badge.master { color: #23527e; border-color: #a9c3df; background: var(--primary-soft); }
    .source-badge.rule { color: #744602; border-color: #e0c074; background: var(--warning-soft); }
    .checkbox-cell { text-align: center; }
    .checkbox-cell label { min-height: 32px; display: inline-flex; align-items: center; justify-content: center; gap: 5px; cursor: pointer; }
    .checkbox-cell input { width: 16px; height: 16px; accent-color: var(--primary); }
    .checkbox-cell span { font-size: 10px; }

    .tabbar { display: flex; gap: 6px; margin-top: 14px; flex-wrap: wrap; }
    .tabbar button { min-height: 38px; padding: 0 12px; border: 1px solid var(--border); border-radius: 5px; background: white; color: var(--text); font-size: 11px; font-weight: 650; display: inline-flex; align-items: center; gap: 6px; }
    .tabbar button[aria-selected="true"] { background: var(--primary); color: white; border-color: var(--primary); }
    .tabbar .validate-action { margin-left: auto; background: var(--accent); color: white; border-color: var(--accent); }
    .count-badge { display: inline-grid; place-items: center; min-width: 18px; height: 18px; padding: 0 5px; border-radius: 999px; background: rgba(255,255,255,.25); font-size: 10px; }

    .settings-source-guide { margin-top: 12px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
    .settings-source-guide > div { padding: 10px 12px; border: 1px solid var(--border); border-radius: var(--radius); background: white; }
    .settings-source-guide strong { font-size: 11px; }
    .settings-source-guide p { margin: 4px 0 0; font-size: 10px; color: var(--text-secondary); }
    .settings-section { margin-top: 16px; border: 1px solid var(--border); border-radius: var(--radius); background: white; overflow: hidden; }
    .settings-section > header { display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: var(--surface-muted); border-bottom: 1px solid var(--border); }
    .settings-section > header div { display: flex; align-items: center; gap: 9px; }
    .settings-section > header span { display: grid; place-items: center; width: 22px; height: 22px; border-radius: 5px; background: var(--primary); color: white; font: 700 11px ui-monospace, monospace; }
    .settings-section > header h3 { margin: 0; font-size: 13px; }
    .settings-section > header p { margin: 0; color: var(--text-secondary); font-size: 10px; }
    .form-grid { margin: 0; padding: 14px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px 14px; }
    .form-grid.compact-grid { grid-template-columns: repeat(2, 1fr); }
    .setting-field { display: grid; gap: 5px; }
    .setting-field > .field-label { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
    .setting-field .field-label > span { font-size: 11px; font-weight: 650; }
    .setting-field .field-label b { color: var(--danger); }
    .setting-field small { color: var(--text-secondary); font-size: 9px; }
    .setting-field input, .setting-field select { width: 100%; height: 36px; padding: 0 9px; border: 1px solid var(--border-strong); border-radius: 4px; background: white; }
    .compound-input { display: flex; gap: 6px; }
    .compound-input.invalid input { border-color: var(--danger); }
    .compound-input select { width: 92px; flex: none; }
    .calculation-route { margin-top: 14px; display: grid; grid-template-columns: repeat(4, 1fr); }
    .calculation-route > div { padding: 12px 14px; border: 1px solid var(--border); border-right: 0; background: var(--primary-soft); }
    .calculation-route > div:first-child { border-radius: var(--radius) 0 0 var(--radius); }
    .calculation-route > div:last-child { border-right: 1px solid var(--border); border-radius: 0 var(--radius) var(--radius) 0; }
    .calculation-route span { font-size: 10px; color: var(--primary-strong); }
    .calculation-route strong { display: block; margin: 4px 0 2px; font: 700 14px ui-monospace, monospace; }
    .calculation-route small { font-size: 9px; color: var(--text-secondary); }
    .calculation-route b { align-self: center; padding: 0 10px; color: var(--primary); font-size: 18px; }
    .legacy-standard-warning, .settings-change-warning { margin-top: 10px; padding: 9px 12px; border: 1px solid var(--warning); border-left: 3px solid var(--warning); border-radius: var(--radius); background: var(--warning-soft); }
    .legacy-standard-warning strong, .settings-change-warning strong { color: #744602; font-size: 11px; }
    .legacy-standard-warning span, .settings-change-warning span { font-size: 10px; color: #5c4a12; }
    .choice-group { margin: 14px 0 0; padding: 12px 14px; border: 1px solid var(--border); border-radius: var(--radius); }
    .choice-group legend { font-size: 11px; font-weight: 700; padding: 0 6px; }
    .choice-group > div { display: flex; flex-wrap: wrap; gap: 14px; margin-top: 8px; }
    .choice-group label { display: inline-flex; align-items: center; gap: 6px; font-size: 11px; }
    .choice-group input { width: 15px; height: 15px; accent-color: var(--primary); }
    .settings-actions { margin-top: 16px; padding-top: 14px; border-top: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; gap: 14px; }
    .settings-actions .form-error { color: var(--danger); font-weight: 650; font-size: 11px; }

    .excel-fidelity-badge { padding: 5px 9px; border: 1px solid var(--border); border-radius: 5px; background: white; color: var(--text-secondary); font-size: 10px; align-self: center; }
    .excel-column-legend { font-size: 10px; color: var(--text-secondary); display: flex; gap: 12px; align-items: center; }
    .legend-dot { width: 9px; height: 9px; border-radius: 50%; display: inline-block; margin-right: 4px; vertical-align: middle; }
    .legend-dot.ok { background: var(--accent); }
    .legend-dot.warn { background: var(--warning); }
    .table-toolbar { display: flex; justify-content: space-between; align-items: center; padding: 9px 12px; border-bottom: 1px solid var(--border); background: var(--surface-muted); font-size: 10px; }
    .excel-footnotes, .shore-excel-notes { margin-top: 10px; padding: 10px 13px; border: 1px solid var(--border); border-radius: var(--radius); background: white; font-size: 10px; color: var(--text-secondary); display: grid; gap: 4px; }
    .excel-footnotes strong, .shore-excel-notes strong { color: var(--primary); }

    .ullage-context-card, .shore-context-card { margin-top: 14px; border: 1px solid var(--border); border-radius: var(--radius); background: white; overflow: hidden; }
    .ullage-context-card > header, .shore-context-card > header { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: var(--primary-soft); border-bottom: 1px solid var(--border); }
    .ullage-context-card h3, .shore-context-card h3 { margin: 0; font-size: 13px; }
    .ullage-source-strip, .shore-context-grid { display: grid; grid-template-columns: repeat(4, 1fr); }
    .ullage-source-strip dl, .shore-context-grid dl { margin: 0; padding: 8px 14px; border-right: 1px solid var(--border); }
    .ullage-source-strip dl:last-child, .shore-context-grid dl:last-child { border-right: 0; }
    .ullage-source-strip dt, .shore-context-grid dt { font-size: 9px; color: var(--text-secondary); }
    .ullage-source-strip dd, .shore-context-grid dd { margin: 2px 0 0; font-size: 12px; font-weight: 650; }
    .shore-context-grid dd select { width: 100%; height: 30px; border: 1px solid var(--border-strong); border-radius: 4px; }
    .ullage-condition-grid { padding: 14px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px 14px; }
    .condition-pair { display: flex; gap: 6px; }
    .condition-pair input { flex: 1; }
    .fw-cell { background: #f3f8f5; }
    .pipeline-row { background: #f6f7f9; }

    .free-water-lineage, .calculation-lineage, .shore-formula-lineage { display: flex; align-items: center; gap: 8px; margin-top: 14px; flex-wrap: wrap; }
    .free-water-lineage > div, .calculation-lineage > div, .shore-formula-lineage > div { padding: 9px 11px; border: 1px solid var(--border); border-radius: 5px; background: white; min-width: 120px; }
    .free-water-lineage span, .calculation-lineage span, .shore-formula-lineage span { display: grid; place-items: center; width: 20px; height: 20px; background: var(--primary); color: white; border-radius: 5px; font: 700 10px ui-monospace; margin-bottom: 4px; }
    .free-water-lineage p, .calculation-lineage p, .shore-formula-lineage p { margin: 0; font-size: 10px; }
    .free-water-lineage p small, .calculation-lineage p small, .shore-formula-lineage p small { color: var(--text-secondary); }
    .free-water-lineage b, .calculation-lineage b, .shore-formula-lineage b { color: var(--primary); font-size: 16px; }
    .lineage-result { border-color: var(--accent) !important; }
    .free-water-import-warning, .formula-notice, .calculation-discrepancy { margin-top: 12px; padding: 10px 13px; border: 1px solid #aac1da; border-left: 3px solid #4f78a5; border-radius: var(--radius); background: #f3f7fb; }
    .free-water-import-warning strong, .formula-notice strong, .calculation-discrepancy strong { font-size: 11px; color: #23527e; }
    .free-water-import-warning span, .formula-notice span, .calculation-discrepancy span { font-size: 10px; color: #46586c; }
    .free-water-context { margin-top: 12px; border: 1px solid var(--border); border-radius: var(--radius); background: white; overflow: hidden; }
    .free-water-context > div { display: grid; grid-template-columns: repeat(4, 1fr); }
    .free-water-context dl { margin: 0; padding: 8px 14px; border-right: 1px solid var(--border); }
    .free-water-context dt { font-size: 9px; color: var(--text-secondary); }
    .free-water-context dd { margin: 2px 0 0; font-size: 12px; font-weight: 650; }
    .imported-fw-value { background: #f3f8f5; }
    .final-fw-value { background: #eef7f2; }
    .trace-value { color: var(--warning); font-weight: 700; }
    .selected-fw-row, .selected-calculation-row { background: #f3f7fb; }
    .calculation-source-guide { display: flex; gap: 14px; margin-top: 10px; font-size: 10px; color: var(--text-secondary); }
    .calc-source { width: 10px; height: 10px; border-radius: 2px; display: inline-block; margin-right: 4px; vertical-align: middle; }
    .calc-source.input { background: #4f78a5; } .calc-source.parameter { background: #a16207; } .calc-source.formula { background: var(--accent); } .calc-source.pending { background: var(--warning); }
    .calculation-basis { margin-top: 12px; border: 1px solid var(--border); border-radius: var(--radius); background: white; overflow: hidden; }
    .calculation-basis header, .calculation-detail-card header, .tank-trace-panel header, .quantity-conversion-card header { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: var(--surface-muted); border-bottom: 1px solid var(--border); }
    .calculation-basis > div { display: grid; grid-template-columns: repeat(3, 1fr); }
    .calculation-basis dl { margin: 0; padding: 8px 14px; border-right: 1px solid var(--border); }
    .calculation-basis dt { font-size: 9px; color: var(--text-secondary); }
    .calculation-basis dd { margin: 2px 0 0; font-size: 12px; font-weight: 650; }
    .calc-chip { display: inline-block; margin-top: 4px; padding: 2px 6px; border-radius: 999px; font-size: 8px; font-weight: 700; }
    .calc-chip.input { color: #23527e; background: var(--primary-soft); }
    .calc-chip.parameter { color: #744602; background: var(--warning-soft); }
    .calc-chip.formula { color: #075d49; background: var(--accent-soft); }
    .calc-chip.pending { color: var(--danger); background: var(--danger-soft); }
    .calculation-detail-table .input-value { background: #f8fbff; }
    .calculation-detail-table .formula-value { background: #f1f6f3; }
    .tank-trace-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; margin-top: 12px; }
    .tank-trace-grid article { padding: 11px; border: 1px solid var(--border); border-radius: 5px; background: white; }
    .tank-trace-grid article span { font-size: 10px; color: var(--text-secondary); }
    .tank-trace-grid article strong { display: block; margin: 4px 0 4px; font: 700 15px ui-monospace, monospace; }
    .tank-trace-grid article p { font-size: 9px; color: var(--text-secondary); margin: 0; }
    .tank-trace-grid b { display: block; text-align: center; color: var(--primary); }
    .quantity-summary-strip { display: flex; align-items: center; gap: 14px; margin-top: 12px; padding: 12px 16px; border: 1px solid var(--border); border-radius: var(--radius); background: white; }
    .quantity-summary-strip dl { margin: 0; }
    .quantity-summary-strip dt { font-size: 9px; color: var(--text-secondary); }
    .quantity-summary-strip dd { margin: 2px 0 0; font-size: 15px; font-weight: 700; font-family: ui-monospace, monospace; }
    .quantity-summary-strip b { color: var(--primary); font-size: 18px; }

    .issues-list { margin-top: 14px; display: grid; gap: 10px; }
    .issues-list article { display: grid; grid-template-columns: 64px 1fr auto; gap: 12px; align-items: center; padding: 12px 14px; border: 1px solid var(--border); border-left: 3px solid var(--warning); border-radius: var(--radius); background: white; }
    .issue-code { display: grid; place-items: center; height: 30px; border-radius: 5px; background: var(--warning-soft); color: #744602; font: 700 11px ui-monospace, monospace; }
    .issues-list h3 { margin: 0; font-size: 12px; }
    .issues-list p { margin: 3px 0 0; font-size: 10px; color: var(--text-secondary); }
    .issues-list button { min-height: 30px; padding: 0 10px; border: 1px solid var(--border); border-radius: 4px; background: white; font-size: 10px; color: var(--primary); }

    .shore-sheet-switch { margin-top: 14px; padding: 10px 14px; border: 1px solid var(--border); border-radius: var(--radius); background: var(--surface-muted); }
    .shore-sheet-switch > div:first-child { font-size: 10px; color: var(--text-secondary); margin-bottom: 8px; }
    .shore-sheet-switch > div:last-child { display: flex; gap: 8px; }
    .shore-sheet-switch button { min-height: 36px; padding: 0 12px; border: 1px solid var(--border); border-radius: 5px; background: white; font-size: 11px; }
    .shore-sheet-switch button[aria-pressed="true"] { background: var(--primary); color: white; border-color: var(--primary); }
    .shore-sheet-switch small { display: block; font-size: 8px; }
    .shore-matrix-table { min-width: 1400px; }
    .shore-matrix-table th, .shore-matrix-table td { font-size: 10px; padding: 4px 7px; }
    .shore-matrix-table .open-column { background: #eef6ef; }
    .shore-matrix-table .close-column { background: #f4f0ea; }
    .shore-matrix-table .shore-section-row th { background: var(--primary-soft); color: var(--primary-strong); font-size: 10px; }
    .field-kind { display: inline-block; padding: 1px 5px; border-radius: 999px; font-size: 8px; font-weight: 700; font-style: normal; }
    .field-kind.input { color: #23527e; background: var(--primary-soft); }
    .field-kind.formula { color: #075d49; background: var(--accent-soft); }
    .shore-result-table .formula-value { background: #f1f6f3; }
    .shore-output-card .number { text-align: right; }

    .calculation-grid { margin-top: 14px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
    .calculation-grid article { padding: 13px; border: 1px solid var(--border); border-radius: var(--radius); background: white; }
    .calculation-grid span { font-size: 10px; color: var(--text-secondary); }
    .calculation-grid h3 { margin: 6px 0 2px; font-size: 13px; }
    .calculation-grid p { margin: 0 0 8px; font-size: 10px; color: var(--text-secondary); }
    .calculation-grid strong { font: 700 16px ui-monospace, monospace; color: var(--primary-strong); }

    .excluded-row { background: #f6f6f8; color: #7b8796; }
    .reason-cell { font-size: 10px; color: var(--text-secondary); }

    .variance-card { margin-top: 14px; border: 1px solid var(--border); border-radius: var(--radius); background: white; overflow: hidden; }
    .variance-card header { display: flex; justify-content: space-between; align-items: center; padding: 11px 14px; background: var(--surface-muted); border-bottom: 1px solid var(--border); }
    .balance-equation { display: flex; align-items: center; gap: 14px; padding: 18px 16px; flex-wrap: wrap; }
    .balance-equation > div { padding: 10px 14px; border: 1px solid var(--border); border-radius: 6px; background: var(--surface-muted); }
    .balance-equation span { font-size: 10px; color: var(--text-secondary); }
    .balance-equation strong { display: block; margin-top: 3px; font: 700 18px ui-monospace, monospace; }
    .balance-equation .result { background: var(--accent-soft); border-color: #8cc9b5; }
    .balance-equation b { color: var(--primary); font-size: 20px; }
    .trace-strip { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding: 10px 16px; background: var(--primary-soft); border-top: 1px solid var(--border); font-size: 11px; }
    .trace-strip b { color: var(--primary); }
    .variance-card > p { padding: 10px 16px; font-size: 10px; color: var(--text-secondary); margin: 0; }

    .report-readiness { margin-top: 14px; padding: 10px 14px; border: 1px solid var(--warning); border-left: 3px solid var(--warning); border-radius: var(--radius); background: var(--warning-soft); }
    .report-readiness strong { color: #744602; font-size: 12px; }
    .report-readiness span { font-size: 10px; color: #5c4a12; }
    .report-list { margin: 12px 0 0; list-style: none; padding: 0; display: grid; gap: 8px; }
    .report-list li { display: grid; grid-template-columns: 38px 1fr auto; gap: 12px; align-items: center; padding: 11px 14px; border: 1px solid var(--border); border-radius: var(--radius); background: white; }
    .report-list li > span { display: grid; place-items: center; width: 30px; height: 30px; border-radius: 6px; background: var(--primary-soft); color: var(--primary-strong); font: 700 11px ui-monospace; }
    .report-list strong { font-size: 13px; }
    .report-list small { display: block; font-size: 10px; color: var(--text-secondary); }
    .report-list em { font-style: normal; font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 999px; }
    .report-list em.partial { color: #744602; background: var(--warning-soft); }
    .report-list em.ready { color: #075d49; background: var(--accent-soft); }
    .report-list em.idle { color: #586474; background: #eef1f4; }
    .overview-card { margin-top: 14px; border: 1px solid var(--border); border-radius: var(--radius); background: white; overflow: hidden; }
    .overview-card header { padding: 10px 14px; background: var(--surface-muted); border-bottom: 1px solid var(--border); }
    .overview-card ul { margin: 0; padding: 12px 14px; list-style: none; display: grid; gap: 8px; }
    .overview-card li { display: flex; gap: 10px; align-items: center; font-size: 12px; }
    .overview-card li > span { display: grid; place-items: center; width: 24px; height: 24px; border-radius: 5px; background: var(--primary-soft); color: var(--primary-strong); font: 700 10px ui-monospace; }
    .bilingual-label { display: inline-block; }
    .bilingual-label strong { font-size: 11px; }
    .bilingual-label small { display: block; font-size: 8px; color: var(--text-secondary); }

    @media (max-width: 860px) {
      .app-shell { grid-template-columns: 64px minmax(0, 1fr); }
      .global-sidebar { padding: 14px 8px; }
      .product-mark { justify-content: center; padding: 0 0 18px; }
      .product-mark > span:last-child, .global-nav em, .offline-card strong, .offline-card small { display: none; }
      .global-nav button { justify-content: center; }
      .workbench-grid { grid-template-columns: 220px minmax(0, 1fr); }
      .workspace { padding: 14px 12px 18px; }
      .topbar { padding: 10px 14px; }
      .project-strip { padding: 8px 14px; }
      .form-grid, .ullage-condition-grid, .settings-source-guide, .ullage-source-strip, .shore-context-grid, .calculation-basis > div, .free-water-context > div, .tank-trace-grid, .calculation-grid, .calculation-route { grid-template-columns: 1fr 1fr; }
    }
    @media (prefers-reduced-motion: reduce) { * { transition-duration: .01ms !important; } }
"""

STEPS = [
    (1, "项目与报告设置", "Project & Report Setup", "已完成", "step-01-project-setup.html"),
    (2, "作业时间线", "Operation Timeline", "14 / 17 项", "step-02-timeline.html"),
    (3, "抵港船舱计量", "Arrival Tank Measurement", "17 / 17 舱", "step-03-arrival-ullage.html"),
    (4, "岸罐接收计量", "Shore Tank Measurement", "6 组 Open / Close", "step-04-shore-tank.html"),
    (5, "卸货后 ROB", "ROB After Discharge", "8 / 17 舱", "step-05-rob.html"),
    (6, "VEF 经验系数", "Vessel Experience Factor", "5 个有效航次", "step-06-vef.html"),
    (7, "数量对比", "Quantity Comparison", "动态计算", "step-07-comparison.html"),
    (8, "报告包", "Report Package", "0 / 8 份", "step-08-reports.html"),
]
PROGRESS = {1: 13, 2: 43, 3: 50, 4: 60, 5: 69, 6: 81, 7: 88, 8: 100}


def workflow_list(current):
    out = []
    for num, zh, en, meta, _ in STEPS:
        state = "done" if num < current else ("active" if num == current else "idle")
        cls = (' class="%s"' % state) if state != "idle" else ""
        cur = ' aria-current="step"' if num == current else ""
        out.append(
            '            <li%s><a href="%s"%s><span class="step-index">%02d</span>'
            '<span class="step-copy"><strong>%s</strong><em>%s</em><small>%s</small></span>'
            '<span class="step-state" aria-hidden="true"></span></a></li>'
            % (cls, STEPS[num - 1][4], cur, num, zh, en, meta)
        )
    return "\n".join(out)


SHELL_HEAD = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>__TITLE__</title>
  <style>__CSS__</style>
</head>
<body>
  <main class="app-shell">
    <a class="skip-link" href="#workspace">跳到主要工作区</a>
    <aside class="global-sidebar" aria-label="主导航">
      <div class="product-mark" aria-label="容量计重离线工作台">
        <span class="mark-square">CQ</span>
        <span><strong>容量计重</strong><small>Quantity Survey · Offline</small></span>
      </div>
      <nav class="global-nav">
        <button type="button"><span>检验任务<small>Inspection Tasks</small></span><em>4</em></button>
        <button type="button" class="selected"><span>作业台<small>Workbench</small></span><em>当前</em></button>
        <button type="button"><span>报告中心<small>Reports</small></span><em>8</em></button>
        <button type="button"><span>基础资料<small>Master Data</small></span><em>24</em></button>
      </nav>
      <div class="offline-card"><span class="status-dot" aria-hidden="true"></span><div><strong>离线模式</strong><small>数据仅保存在本机</small></div></div>
    </aside>
    <section class="main-stage">
      <header class="topbar">
        <div><div class="breadcrumb">项目 / 卸货检验 / 210225050087</div><h1>MT SAIQ · 卸货检验</h1></div>
        <div class="topbar-meta">
          <span class="project-state">现场作业中</span>
          <span class="save-state" id="saveState">草稿已保存</span>
          <button type="button" class="button secondary" id="saveDraftBtn">保存草稿</button>
          <button type="button" class="button primary" id="reportBtn">报告预览</button>
        </div>
      </header>
      <div class="project-strip">
        <dl><dt>COMMODITY <small>货物</small></dt><dd>OMAN EXPORT BLEND CRUDE OIL</dd></dl>
        <dl><dt>PORT / TERMINAL <small>港口 / 码头</small></dt><dd>营口港 · 仙人岛原油码头</dd></dl>
        <dl><dt>MEASUREMENT STANDARD <small>计量标准</small></dt><dd>2004 / API MPMS 11.5 (2013)</dd></dl>
        <dl><dt>INSPECTION DATE <small>检验日期</small></dt><dd>2025-05-24 — 2025-05-26</dd></dl>
      </div>
      <div class="workbench-grid">
        <aside class="workflow-panel" aria-label="卸货检验步骤">
          <div class="panel-heading">
            <div><p class="eyebrow">Workflow · 流程进度</p><h2>Discharge Survey <small>卸货检验</small></h2></div>
            <strong id="progressLabel">__PROGRESS__%</strong>
          </div>
          <div class="progress-track" aria-label="整体完成度 __PROGRESS__%"><span id="progressBar" style="width: __PROGRESS__%"></span></div>
          <ol class="workflow-list">
__WORKFLOW__
          </ol>
        </aside>
        <section class="workspace" id="workspace">
__BODY__
        </section>
      </div>
    </section>
  </main>
  <script>
__JS__
  </script>
</body>
</html>
"""

COMMON_JS = r"""
    const fmt = (v, d = 3) => new Intl.NumberFormat('zh-CN', { minimumFractionDigits: d, maximumFractionDigits: d }).format(v);
    const saveStateEl = document.getElementById('saveState');
    function flash(msg) { if (!saveStateEl) return; saveStateEl.textContent = msg; setTimeout(() => { saveStateEl.textContent = '草稿已保存'; }, 1800); }
    const sd = document.getElementById('saveDraftBtn'); if (sd) sd.addEventListener('click', () => flash('草稿已保存（演示）'));
    const rb = document.getElementById('reportBtn');
    if (rb) rb.addEventListener('click', () => { __REPORTBTN__ });
"""


# ---------------- STEP 01 ----------------
def step01():
    body = r"""
          <div class="workspace-heading settings-heading">
            <div><p class="eyebrow">步骤 01</p><h2>项目与报告设置</h2><p>对应原 Excel 的 Cover 与“报告首选项”：先确定公共信息、计算口径和报告范围，再进入现场计量。</p></div>
            <div class="context-actions"><button type="button" class="button tertiary" onclick="alert('历史项目复制应只复制公共信息和设置，不复制测量读数、计算结果与签发记录。')">从历史项目复制</button><button type="button" class="button secondary" onclick="alert('（演示）跳转到基础资料管理')">管理基础资料</button></div>
          </div>
          <div class="settings-source-guide" aria-label="字段来源说明">
            <div><span class="source-badge project">项目填写</span><p>每个作业单独填写，例如作业号、日期和航次。</p></div>
            <div><span class="source-badge master">基础资料</span><p>从客户、船舶、港口等主数据选择，可申请临时覆盖。</p></div>
            <div><span class="source-badge rule">系统规则</span><p>由管理员维护版本，普通用户只能选择有效版本。</p></div>
          </div>
          <form class="settings-form" onsubmit="applySettings(event)">
            <section class="settings-section">
              <header><div><span>01</span><h3>基本信息</h3></div><p>项目级数据</p></header>
              <div class="form-grid">
                <label class="setting-field"><span class="field-label"><span>作业号 <b>*</b></span></span><input id="jobNo" value="210225050087" /></label>
                <label class="setting-field"><span class="field-label"><span>报告日期 <b>*</b></span></span><input type="date" id="reportDate" value="2025-05-26" /></label>
                <label class="setting-field"><span class="field-label"><span>检验开始 <b>*</b></span></span><input type="datetime-local" id="inspectionStart" value="2025-05-24T08:20" /></label>
                <label class="setting-field"><span class="field-label"><span>检验结束</span></span><input type="datetime-local" id="inspectionEnd" value="2025-05-26T18:00" /></label>
                <label class="setting-field"><span class="field-label"><span>作业类型 <b>*</b></span></span><select id="operationType"><option value="DISCHARGE" selected>卸货检验</option><option value="LOAD">装货检验</option><option value="STS">船对船 STS</option><option value="ITT">罐对罐 ITT</option></select></label>
                <label class="setting-field"><span class="field-label"><span>航次</span></span><input id="voyageNo" value="SAIQ-2505" /></label>
              </div>
            </section>
            <section class="settings-section">
              <header><div><span>02</span><h3>参与方与作业地点</h3></div><p>选择基础资料并冻结项目快照</p></header>
              <div class="form-grid">
                <label class="setting-field"><span class="field-label"><span>委托方（中文） <b>*</b></span><em class="source-badge master">基础资料</em></span><select id="clientName"><option>中国石油国际事业有限公司</option><option>中国石化燃料油销售有限公司</option></select></label>
                <label class="setting-field"><span class="field-label"><span>委托方（英文）</span></span><input id="clientNameEn" value="PETROCHINA INTERNATIONAL CO., LTD." /></label>
                <label class="setting-field"><span class="field-label"><span>船舶 <b>*</b></span><em class="source-badge master">基础资料</em></span><select id="vesselName"><option>MT SAIQ</option><option>MT OCEAN PEARL</option></select></label>
                <label class="setting-field"><span class="field-label"><span>港口 <b>*</b></span><em class="source-badge master">基础资料</em></span><select id="portName"><option>营口港</option><option>青岛港</option><option>宁波港</option></select></label>
                <label class="setting-field"><span class="field-label"><span>码头 / 油库 <b>*</b></span><em class="source-badge master">基础资料</em></span><select id="terminalName"><option>仙人岛原油码头</option><option>其他码头</option></select></label>
                <label class="setting-field"><span class="field-label"><span>项目快照</span><em class="source-badge rule">系统规则</em></span><input value="保存时冻结名称、版本及关联参数" readonly /></label>
              </div>
            </section>
            <section class="settings-section">
              <header><div><span>03</span><h3>货物与计算参数</h3></div><p>关键字段变化需要重新计算</p></header>
              <div class="form-grid">
                <label class="setting-field"><span class="field-label"><span>货物名称（中文） <b>*</b></span><em class="source-badge master">基础资料</em></span><select id="cargoName"><option>阿曼出口混合原油</option><option>沙特轻质原油</option></select></label>
                <label class="setting-field"><span class="field-label"><span>货物名称（英文）</span></span><input id="cargoNameEn" value="OMAN EXPORT BLEND CRUDE OIL" readonly /></label>
                <label class="setting-field"><span class="field-label"><span>油品类别 <b>*</b></span><em class="source-badge rule">系统规则</em></span><select id="cargoCategory"><option value="A" selected>A · 原油</option><option value="B">B · 成品油</option><option value="C">C · 特殊/未知应用</option><option value="D">D · 润滑油</option></select></label>
                <label class="setting-field"><span class="field-label"><span>密度类型 <b>*</b></span><em class="source-badge rule">系统规则</em></span><select id="densityType"><option value="DENSITY_15C" selected>密度 @15℃</option><option value="DENSITY_20C">密度 @20℃</option><option value="API">API Gravity @60℉</option><option value="SG_60F">相对密度 SG 60/60℉</option></select></label>
                <label class="setting-field"><span class="field-label"><span>密度值 <b>*</b></span><em class="source-badge project">项目填写</em></span><span class="compound-input" id="densityWrap"><input id="densityValue" type="number" step="0.0001" value="0.8598" /><select id="densityUnit"><option>g/cm³</option><option>kg/m³</option></select></span></label>
                <label class="setting-field"><span class="field-label"><span>VCF 标准 <b>*</b></span><em class="source-badge rule">系统规则</em></span><select id="vcfStandard"><option value="ASTM D1250 / API MPMS 11.1" selected>ASTM D1250 / API MPMS 11.1</option><option value="GB/T 1885">GB/T 1885</option><option value="ASTM-IP Petroleum Measurement Tables">ASTM-IP Petroleum Measurement Tables</option></select></label>
                <label class="setting-field"><span class="field-label"><span>VCF 版本 <b>*</b></span><em class="source-badge rule">系统规则</em></span><select id="vcfVersion"><option>2004</option><option>1980</option></select></label>
                <label class="setting-field"><span class="field-label"><span>WCF 标准</span><em class="source-badge rule">系统规则</em></span><select id="wcfStandard"><option>API MPMS 11.5 (2013)</option><option>ASTM D1250 (1980)</option></select></label>
                <label class="setting-field"><span class="field-label"><span>沉淀物和水 S&amp;W %</span></span><input id="sedimentWaterPct" type="number" min="0" max="100" step="0.01" value="0.12" /></label>
                <label class="setting-field"><span class="field-label"><span>允许船岸差率 %</span><em class="source-badge rule">系统规则</em></span><input id="allowedVariancePct" type="number" min="0" step="0.001" value="0.3" /></label>
              </div>
              <div class="calculation-route" aria-label="当前 VCF 计算路径" id="calcRoute"></div>
            </section>
            <section class="settings-section">
              <header><div><span>04</span><h3>报告输出设置</h3></div><p>替代 Excel 的报告首选项</p></header>
              <div class="form-grid compact-grid">
                <label class="setting-field"><span class="field-label"><span>报告语言</span></span><select id="reportLanguage"><option value="ZH_EN" selected>中英文</option><option value="ZH">仅中文</option><option value="EN">仅英文</option></select></label>
                <label class="setting-field"><span class="field-label"><span>报告类型</span></span><select id="reportType"><option value="FIELD">现场报告</option><option value="FINAL" selected>正式报告</option></select></label>
              </div>
              <fieldset class="choice-group"><legend>报告数量单位 <span class="source-badge rule">系统规则</span></legend><div id="unitChoices"></div></fieldset>
              <fieldset class="choice-group"><legend>报告包组成 <span class="source-badge project">项目填写</span></legend><div id="reportChoices"></div></fieldset>
            </section>
            <footer class="settings-actions"><div><span id="settingsHint">应用后，顶部摘要、报告预览和后续计算将使用本项目设置。</span></div><button type="submit" class="button primary">保存并应用设置</button></footer>
          </form>
"""
    js = r"""
    const densityRules = {
      DENSITY_15C: { label: "密度 @15℃", units: ["g/cm³", "kg/m³"], step: "0.0001", family: "54" },
      DENSITY_20C: { label: "密度 @20℃", units: ["g/cm³", "kg/m³"], step: "0.0001", family: "60" },
      API: { label: "API Gravity @60℉", units: ["°API"], step: "0.01", family: "6" },
      SG_60F: { label: "相对密度 SG 60/60℉", units: ["SG"], step: "0.0001", family: "24" }
    };
    const vcfVersions = {
      "ASTM D1250 / API MPMS 11.1": ["2004", "1980"],
      "GB/T 1885": ["1998"],
      "ASTM-IP Petroleum Measurement Tables": ["1952"]
    };
    const unitOptions = [["M3_15C", "m³ @15℃"], ["M3_20C", "m³ @20℃"], ["BBL_60F", "bbl @60℉"], ["MT_AIR", "公吨（空气中）"], ["LT_AIR", "长吨（空气中）"]];
    const reportOptions = [["QUANTITY", "数量证书"], ["VESSEL", "船舱计量"], ["SHORE", "岸罐计量"], ["COMPARISON", "船岸差异"], ["ROB", "ROB"], ["VEF", "VEF"], ["TIME", "时间记录"], ["SAMPLE", "取样报告"]];
    const settings = {
      densityType: "DENSITY_15C", densityValue: "0.8598", densityUnit: "g/cm³",
      vcfStandard: "ASTM D1250 / API MPMS 11.1", vcfVersion: "2004",
      cargoCategory: "A", quantityUnits: ["M3_15C", "MT_AIR"], selectedReports: ["QUANTITY", "VESSEL", "SHORE", "COMPARISON", "ROB", "VEF", "TIME", "SAMPLE"]
    };
    function renderCalcRoute() {
      const rule = densityRules[settings.densityType];
      const tableCode = rule.family + settings.cargoCategory;
      const targetBases = [settings.quantityUnits.includes("M3_15C") ? "15℃" : "", settings.quantityUnits.includes("M3_20C") ? "20℃" : "", settings.quantityUnits.includes("BBL_60F") ? "60℉" : ""].filter(Boolean);
      document.getElementById("calcRoute").innerHTML =
        '<div><span>输入口径</span><strong>' + rule.label + '</strong><small>' + (settings.densityValue ? settings.densityValue + ' ' + settings.densityUnit : '等待输入密度值') + '</small></div><b>→</b>' +
        '<div><span>油品与表族</span><strong>' + settings.cargoCategory + ' 类 · Table ' + tableCode + '</strong><small>' + (settings.cargoCategory === 'A' ? '通用原油' : settings.cargoCategory === 'B' ? '通用成品油' : settings.cargoCategory === 'C' ? '特殊应用' : '润滑油') + '</small></div><b>→</b>' +
        '<div><span>算法标准</span><strong>' + settings.vcfVersion + ' 版</strong><small>' + settings.vcfStandard + '</small></div><b>→</b>' +
        '<div><span>报告目标</span><strong>' + (targetBases.length ? targetBases.join(' / ') : '未选择') + '</strong><small>由报告数量单位决定</small></div>';
    }
    function renderChoices() {
      document.getElementById("unitChoices").innerHTML = unitOptions.map(([v, l]) =>
        '<label><input type="checkbox" ' + (settings.quantityUnits.includes(v) ? 'checked' : '') + ' data-grp="unit" value="' + v + '"><span>' + l + '</span></label>').join('');
      document.getElementById("reportChoices").innerHTML = reportOptions.map(([v, l]) =>
        '<label><input type="checkbox" ' + (settings.selectedReports.includes(v) ? 'checked' : '') + ' data-grp="report" value="' + v + '"><span>' + l + '</span></label>').join('');
    }
    document.getElementById("densityType").addEventListener("change", (e) => {
      const r = densityRules[e.target.value]; settings.densityType = e.target.value; settings.densityUnit = r.units[0]; settings.densityValue = "";
      document.getElementById("densityValue").value = ""; document.getElementById("densityUnit").innerHTML = r.units.map(u => '<option>' + u + '</option>').join(''); renderCalcRoute();
    });
    document.getElementById("vcfStandard").addEventListener("change", (e) => {
      const vs = vcfVersions[e.target.value]; settings.vcfStandard = e.target.value; settings.vcfVersion = vs[0];
      document.getElementById("vcfVersion").innerHTML = vs.map(v => '<option>' + v + '</option>').join(''); renderCalcRoute();
    });
    ["densityValue", "cargoCategory", "vcfVersion"].forEach(id => document.getElementById(id).addEventListener("input", (e) => { settings[id] = e.target.value; renderCalcRoute(); }));
    document.getElementById("unitChoices").addEventListener("change", (e) => { const v = e.target.value; settings.quantityUnits = e.target.checked ? [...settings.quantityUnits, v] : settings.quantityUnits.filter(x => x !== v); renderCalcRoute(); });
    document.getElementById("reportChoices").addEventListener("change", (e) => { const v = e.target.value; settings.selectedReports = e.target.checked ? [...settings.selectedReports, v] : settings.selectedReports.filter(x => x !== v); });
    function applySettings(e) { e.preventDefault(); flash('设置已应用（演示）'); }
    renderCalcRoute(); renderChoices();
"""
    return body, js


# ---------------- STEP 03 ----------------
def step03():
    body = r"""
          <div class="workspace-heading ullage-heading">
            <div><p class="eyebrow">STEP 03 · EXCEL SHEET「ULLAGE」</p><h2>Arrival Tank Measurement <small>抵港船舱计量</small></h2><p>保留 Excel 英文原字段，并在同一位置显示中文翻译；Gauge、Free Water、体积换算及总计字段均不删减。</p></div>
            <div class="context-actions"><span class="excel-fidelity-badge">Excel Original + 中文翻译</span><button type="button" class="button tertiary" onclick="document.getElementById('ullage-conditions').scrollIntoView({behavior:'smooth'})">Measurement Conditions<br><small>计量条件</small></button><button type="button" class="button tertiary" onclick="alert('批量导入将按 Ullage 页原列结构校验；原型阶段暂未接入文件写入。')">Batch Import<br><small>批量导入</small></button></div>
          </div>
          <section class="ullage-context-card" id="ullage-conditions" aria-labelledby="ullage-context-title">
            <header><div><span>Excel 报告头</span><h3 id="ullage-context-title">ULLAGE REPORT · Before Discharging</h3></div><p><span class="source-badge project">项目填写</span> 可编辑并随草稿保存</p></header>
            <div class="ullage-source-strip">
              <dl><dt>JOB NO.<small>作业号</small></dt><dd>210225050087</dd></dl>
              <dl><dt>COMMODITY<small>货物</small></dt><dd>OMAN EXPORT BLEND CRUDE OIL</dd></dl>
              <dl><dt>VESSEL<small>船舶</small></dt><dd>MT SAIQ</dd></dl>
              <dl><dt>PORT / TERMINAL<small>港口 / 码头</small></dt><dd>营口港 · 仙人岛原油码头</dd></dl>
            </div>
            <div class="ullage-condition-grid" id="ullageConditions"></div>
          </section>
          <div class="metric-row ullage-metrics" id="ullageMetrics" aria-label="船舱计量汇总"></div>
          <div class="tabbar" role="tablist" aria-label="计量工作区视图">
            <button type="button" role="tab" aria-selected="true" data-panel="entry" onclick="switchPanel('entry')">Data Entry <small>数据录入</small></button>
            <button type="button" role="tab" aria-selected="false" data-panel="freeWater" onclick="switchPanel('freeWater')">Free Water Determination <small>游离水测定</small></button>
            <button type="button" role="tab" aria-selected="false" data-panel="calculation" onclick="switchPanel('calculation')">Calculation Details <small>计算明细</small></button>
            <button type="button" role="tab" aria-selected="false" data-panel="issues" onclick="switchPanel('issues')">Validation Issues <small>校验问题</small></button>
            <button type="button" class="validate-action" onclick="alert('（演示）运行校验：3 项业务待确认')">Run Validation <small>运行校验</small></button>
          </div>
          <div id="panel-entry"></div>
          <div id="panel-freeWater" hidden></div>
          <div id="panel-calculation" hidden></div>
          <div id="panel-issues" hidden></div>
          <footer class="workspace-footer">
            <div><strong>下一步：岸罐接收计量</strong><span>本机草稿会保留各步骤录入状态，可随时返回修改</span></div>
            <a class="button primary" href="step-04-shore-tank.html">保存并进入下一步</a>
          </footer>
"""
    js = r"""
    const conditions = { reportStage: "Before Discharging", inspectionDate: "2025-05-24", inspectionTime: "18:42", seaCondition: "Calm", levelDetectedBy: "UTI", utiSerialNo: "G17468", draftFwd: 19.8, draftAft: 19.8, trim: 0, trimState: "Even Keel", list: 0, listState: "Upright", fwDetectedBy: "UTI & Water Finding Paste", waterPasteBrand: "UNIVERSAL WATER FINDER PASTE", densityAt20: 0.8461, densitySuppliedBy: "LOADING PORT", applicant: "", clientReference: "" };
    const condFields = [["reportStage","REPORT STAGE","报告阶段"],["inspectionDate","DATE OF INSPECTION","检验日期"],["inspectionTime","TIME","检验时间"],["seaCondition","SEA CONDITION","海况"],["levelDetectedBy","LEVEL DETECTED BY","液位检测仪器/方式"],["utiSerialNo","UTI SER. NO.","UTI 仪器序列号"],["draftFwd","DRAFT FWD. (m)","艏吃水"],["draftAft","DRAFT AFT. (m)","艉吃水"],["trim","TRIM (m)","纵倾及状态"],["list","LIST (m)","横倾及状态"],["fwDetectedBy","F.W. DETECTED BY","游离水检测方式"],["waterPasteBrand","BRAND OF WATER FINDING PASTE","试水膏品牌"],["densityAt20","DENSITY @20℃ (g/cm³)","20℃ 密度"],["densitySuppliedBy","SUPPLIED BY","密度数据提供方"],["applicant","APPLICANT","申请方"],["clientReference","CLIENT'S REF. NO.","客户参考号"]];
    const rows = [
      { id: 1, tank: "1C", hatch: "A", gaugeMethod: "U", observed: 4.020, corrected: 4.020, temperature: 16.7, tov: 154014.17, fwMethod: "I", fwInterface: 0.070, freeWater: 431.67, vcf: 0.99855, fwSource: "ULLAGE_IMPORTED" },
      { id: 2, tank: "2C", hatch: "A", gaugeMethod: "U", observed: 3.940, corrected: 3.940, temperature: 16.6, tov: 190253.54, fwMethod: "I", fwInterface: 0.010, freeWater: 79.88, vcf: 0.99864, fwSource: "ULLAGE_IMPORTED" },
      { id: 3, tank: "3C", hatch: "A", gaugeMethod: "U", observed: 4.910, corrected: 4.910, temperature: 16.8, tov: 182954.22, fwMethod: "I", fwInterface: 0.010, freeWater: 79.88, vcf: 0.99847, fwSource: "ULLAGE_IMPORTED" },
      { id: 4, tank: "4C", hatch: "A", gaugeMethod: "U", observed: 3.840, corrected: 3.840, temperature: 17.0, tov: 191004.55, fwMethod: "I", fwInterface: 0.040, freeWater: 305.06, vcf: 0.99830, fwSource: "ULLAGE_IMPORTED" },
      { id: 5, tank: "5C", hatch: "A", gaugeMethod: "U", observed: 3.740, corrected: 3.740, temperature: 16.9, tov: 186499.16, fwMethod: "I", fwInterface: "TRACE", freeWater: 0, vcf: 0.99838, fwSource: "ULLAGE_IMPORTED" },
      { id: 6, tank: "1P", hatch: "A", gaugeMethod: "U", observed: 3.570, corrected: 3.570, temperature: 17.0, tov: 86450.29, fwMethod: "I", fwInterface: 0.050, freeWater: 67.93, vcf: 0.99830, fwSource: "ULLAGE_IMPORTED" },
      { id: 7, tank: "1S", hatch: "A", gaugeMethod: "U", observed: 3.560, corrected: 3.560, temperature: 16.9, tov: 86489.92, fwMethod: "I", fwInterface: 0.040, freeWater: 55.35, vcf: 0.99838, fwSource: "ULLAGE_IMPORTED" },
      { id: 8, tank: "2P", hatch: "A", gaugeMethod: "U", observed: 3.920, corrected: 3.920, temperature: 17.0, tov: 114960.12, fwMethod: "I", fwInterface: 0.040, freeWater: 133.66, vcf: 0.99830, fwSource: "ULLAGE_IMPORTED" },
      { id: 9, tank: "2S", hatch: "A", gaugeMethod: "U", observed: 3.900, corrected: 3.900, temperature: 17.0, tov: 115056.35, fwMethod: "I", fwInterface: 0.030, freeWater: 101.58, vcf: 0.99830, fwSource: "ULLAGE_IMPORTED" },
      { id: 10, tank: "3P", hatch: "A", gaugeMethod: "U", observed: 3.830, corrected: 3.830, temperature: 17.1, tov: 89488.90, fwMethod: "I", fwInterface: 0.020, freeWater: 54.72, vcf: 0.99821, fwSource: "ULLAGE_IMPORTED" },
      { id: 11, tank: "3S", hatch: "A", gaugeMethod: "U", observed: 3.830, corrected: 3.830, temperature: 17.2, tov: 89488.90, fwMethod: "I", fwInterface: 0.020, freeWater: 54.72, vcf: 0.99813, fwSource: "ULLAGE_IMPORTED" },
      { id: 12, tank: "4P", hatch: "A", gaugeMethod: "U", observed: 3.930, corrected: 3.930, temperature: 17.6, tov: 114887.78, fwMethod: "I", fwInterface: 0.060, freeWater: 198.13, vcf: 0.99779, fwSource: "ULLAGE_IMPORTED" },
      { id: 13, tank: "4S", hatch: "A", gaugeMethod: "U", observed: 3.920, corrected: 3.920, temperature: 18.4, tov: 114935.59, fwMethod: "I", fwInterface: 0.090, freeWater: 295.62, vcf: 0.99710, fwSource: "ULLAGE_IMPORTED" },
      { id: 14, tank: "5P", hatch: "A", gaugeMethod: "U", observed: 3.900, corrected: 3.900, temperature: 21.4, tov: 70315.04, fwMethod: "I", fwInterface: 0.070, freeWater: 107.18, vcf: 0.99455, fwSource: "ULLAGE_IMPORTED" },
      { id: 15, tank: "5S", hatch: "A", gaugeMethod: "U", observed: 3.900, corrected: 3.900, temperature: 17.4, tov: 70315.04, fwMethod: "I", fwInterface: 0.130, freeWater: 195.74, vcf: 0.99796, fwSource: "ULLAGE_IMPORTED" },
      { id: 16, tank: "SLOP P", hatch: "A", gaugeMethod: "U", observed: 3.260, corrected: 3.260, temperature: 96.6, tov: 24971.17, fwMethod: "I", fwInterface: 0.560, freeWater: 36.48, vcf: 0.92934, fwSource: "ULLAGE_IMPORTED" },
      { id: 17, tank: "SLOP S", hatch: "A", gaugeMethod: "U", observed: 3.200, corrected: 3.200, temperature: 96.1, tov: 25066.78, fwMethod: "I", fwInterface: 0.510, freeWater: 32.71, vcf: 0.92978, fwSource: "ULLAGE_IMPORTED" },
      { id: 18, tank: "P.Line", hatch: "A", gaugeMethod: "U", observed: 0, corrected: 0, temperature: "", tov: 0, fwMethod: "I", fwInterface: 0, freeWater: 0, vcf: 1.01271, fwSource: "ULLAGE_IMPORTED", assetType: "PIPELINE" }
    ];
    const cargoTanks = rows.filter(r => r.assetType !== "PIPELINE");
    const vcfVersion = "2004";
    const excelStandardDensity15 = 849.7, excelSandWaterPct = 0.025, excelWcfMtAir = 0.848627984;
    const netFactor = 1 - excelSandWaterPct / 100;
    const quantityConversions = [
      { label: "US Barrels (60℉)", zh: "60℉ 美制桶", factor: 6.292768373, digits: 2 },
      { label: "Cubic Meters (15℃)", zh: "15℃ 标准立方米", factor: 1, digits: 3 },
      { label: "Metric Tons (in air)", zh: "空气中公吨", factor: excelWcfMtAir, digits: 3 },
      { label: "Long Tons (in air)", zh: "空气中长吨", factor: 0.8352252017, digits: 3 }
    ];
    let selectedCalculationId = rows[0].id;
    function totals() { return rows.reduce((s, r) => { const gov = Math.max(r.tov - r.freeWater, 0); return { tov: s.tov + r.tov, fw: s.fw + r.freeWater, gov: s.gov + gov, gsv: s.gsv + gov * r.vcf }; }, { tov: 0, fw: 0, gov: 0, gsv: 0 }); }
    function upd(id, field, val) { const r = rows.find(x => x.id === id); if (r) r[field] = (field === "observed" || field === "corrected" || field === "tov" || field === "vcf") ? Number(val) : (field === "temperature" ? (val === "" ? "" : Number(val)) : val); renderEntry(); renderMetrics(); }
    function updFW(id, field, val) {
      const r = rows.find(x => x.id === id); if (!r) return;
      if (field === "utiGauge" || field === "pasteGauge") { r[field] = (val.trim().toUpperCase() === "TRACE" || val === "") ? val : Number(val); }
      else if (field === "utiVolume" || field === "pasteVolume") { r[field] = val === "" ? "" : Number(val); }
      else r[field] = val;
      const method = r.determinationMethod;
      if (method === "UTI" && typeof r.utiGauge === "number" && typeof r.utiVolume === "number") { r.fwInterface = r.utiGauge; r.freeWater = r.utiVolume; r.fwSource = "DETERMINATION"; }
      else if (method === "PASTE" && typeof r.pasteGauge === "number" && typeof r.pasteVolume === "number") { r.fwInterface = r.pasteGauge; r.freeWater = r.pasteVolume; r.fwSource = "DETERMINATION"; }
      else if (method === "AVERAGE" && typeof r.utiGauge === "number" && typeof r.pasteGauge === "number" && typeof r.utiVolume === "number" && typeof r.pasteVolume === "number") { r.fwInterface = Math.round((r.utiGauge + r.pasteGauge) / 2 * 1000) / 1000; r.freeWater = Math.round((r.utiVolume + r.pasteVolume) / 2 * 1000) / 1000; r.fwSource = "DETERMINATION"; }
      renderFreeWater(); renderMetrics();
    }
    function switchPanel(p) { ["entry", "freeWater", "calculation", "issues"].forEach(x => { document.getElementById("panel-" + x).hidden = x !== p; }); document.querySelectorAll(".tabbar button[data-panel]").forEach(b => b.setAttribute("aria-selected", b.dataset.panel === p ? "true" : "false")); }
    function renderConditions() {
      document.getElementById("ullageConditions").innerHTML = condFields.map(([k, en, zh]) => {
        const isNum = ["draftFwd", "draftAft", "trim", "list", "densityAt20"].includes(k);
        return '<label class="setting-field"><span class="field-label"><span class="bilingual-label"><strong>' + en + '</strong><small>' + zh + '</small></span></span>' +
          (isNum ? '<input type="number" step="0.01" id="c_' + k + '" value="' + conditions[k] + '" onchange="conditions[\'' + k + '\']=Number(this.value);">' : '<input id="c_' + k + '" value="' + (conditions[k] ?? "") + '" onchange="conditions[\'' + k + '\']=this.value;">') + '</label>';
      }).join('');
    }
    function renderMetrics() {
      const t = totals(); const fwPct = t.tov === 0 ? 0 : t.fw / t.tov * 100;
      document.getElementById("ullageMetrics").innerHTML =
        '<article><span>Cargo Tank Records · 货油舱记录</span><strong>' + cargoTanks.length + ' / 17</strong><small>另含 1 条 P.Line 管线记录</small></article>' +
        '<article><span>Total Observed Volume · 总观测体积</span><strong>' + fmt(t.tov, 2) + '</strong><small>m³ · TOV</small></article>' +
        '<article><span>Total Free Water Volume · 游离水总体积</span><strong>' + fmt(t.fw, 2) + '</strong><small>m³ · 占 TOV ' + fwPct.toFixed(3) + '%</small></article>' +
        '<article class="metric-accent"><span>Gross Standard Volume · 标准毛体积</span><strong>' + fmt(t.gsv, 3) + '</strong><small>m³ @15℃ · GSV</small></article>';
    }
    function renderEntry() {
      const t = totals();
      const head = '<thead><tr class="group-header"><th rowSpan="2">Tank No.<small>舱号</small></th><th rowSpan="2">G.H.L. (1)<small>检尺口位置</small></th><th colSpan="3">Gauge<small>液位测量</small></th><th rowSpan="2">Temp.<small>平均温度 · ℃</small></th><th rowSpan="2">Total Observed Volume<small>总观测体积 · m³</small></th><th colSpan="3" class="fw-group">Free Water<small>游离水</small></th><th rowSpan="2">Gross Observed Volume<small>观测毛体积 · m³</small></th><th rowSpan="2">VCF · T-54A<small>体积修正系数 · Ver. ' + vcfVersion + '</small></th><th rowSpan="2">Gross Standard Volume<small>标准毛体积 · m³ (15℃)</small></th><th rowSpan="2">Status<small>状态</small></th></tr>' +
        '<tr><th>U/I (2)<small>空距 / 实高</small></th><th>Obs\'d<small>观测值 · m</small></th><th>Corr\'d<small>修正值 · m</small></th><th class="fw-group">U/I (2)<small>空距 / 实高</small></th><th class="fw-group">Interface<small>水界面高度 · m</small></th><th class="fw-group">Volume<small>水体积 · m³</small></th></tr></thead>';
      const body = '<tbody>' + rows.map(r => {
        const gov = Math.max(r.tov - r.freeWater, 0); const trace = r.fwInterface === "TRACE";
        const cls = r.assetType === "PIPELINE" ? ' class="pipeline-row"' : '';
        return '<tr' + cls + '>' +
          '<th scope="row"><span>' + r.tank + '</span>' + (r.assetType === "PIPELINE" ? '<small>管线</small>' : '') + '</th>' +
          '<td><select aria-label="' + r.tank + ' 检尺口位置" onchange="upd(' + r.id + ',`hatch`,this.value)"><option value="F">F</option><option value="C">C</option><option value="A"' + (r.hatch === "A" ? " selected" : "") + '>A</option></select></td>' +
          '<td><select aria-label="' + r.tank + ' 液位测量方式" onchange="upd(' + r.id + ',`gaugeMethod`,this.value)"><option value="U"' + (r.gaugeMethod === "U" ? " selected" : "") + '>U</option><option value="I"' + (r.gaugeMethod === "I" ? " selected" : "") + '>I</option></select></td>' +
          '<td><input aria-label="' + r.tank + ' 观测液位" type="number" step="0.001" value="' + r.observed + '" onchange="upd(' + r.id + ',`observed`,this.value)"></td>' +
          '<td><input aria-label="' + r.tank + ' 修正液位" type="number" step="0.001" value="' + r.corrected + '" onchange="upd(' + r.id + ',`corrected`,this.value)"></td>' +
          '<td><input aria-label="' + r.tank + ' 温度" type="number" step="0.1" value="' + r.temperature + '" onchange="upd(' + r.id + ',`temperature`,this.value)"></td>' +
          '<td><input aria-label="' + r.tank + ' TOV" type="number" step="0.01" value="' + r.tov + '" onchange="upd(' + r.id + ',`tov`,this.value)"></td>' +
          '<td class="fw-cell linked-result">' + r.fwMethod + '<small>测定结果</small></td>' +
          '<td class="fw-cell linked-result ' + (trace ? "trace-value" : "") + '">' + (r.fwInterface === "" ? "—" : r.fwInterface) + '<small>来自 FW 测定</small></td>' +
          '<td class="fw-cell linked-result number">' + fmt(r.freeWater, 2) + '<small>' + (r.fwSource === "DETERMINATION" ? "已联动" : "Ullage 导入") + '</small></td>' +
          '<td class="calculated number">' + fmt(gov, 2) + '</td>' +
          '<td><input aria-label="' + r.tank + ' VCF" type="number" step="0.00001" value="' + r.vcf + '" onchange="upd(' + r.id + ',`vcf`,this.value)"></td>' +
          '<td class="calculated number strong">' + fmt(gov * r.vcf, 3) + '</td>' +
          '<td class="fw-row-action"><span class="status-pill ' + (trace || r.fwSource !== "DETERMINATION" ? "warning" : "success") + '">' + (trace ? "TRACE" : r.assetType === "PIPELINE" ? "管线记录" : r.fwSource === "DETERMINATION" ? "已判定" : "待补测定依据") + '</span></td></tr>';
      }).join('') +
        '<tfoot><tr><th scope="row" colSpan="6">TOTAL · 17 舱 + P.Line</th><td>' + fmt(t.tov, 2) + '</td><td colSpan="2">—</td><td>' + fmt(t.fw, 2) + '</td><td>' + fmt(t.gov, 2) + '</td><td>—</td><td>' + fmt(t.gsv, 3) + '</td><td>3 项待确认</td></tr></tfoot>';
      document.getElementById("panel-entry").innerHTML = '<div class="table-card ullage-table-card"><div class="table-toolbar"><div class="excel-column-legend"><strong>列结构与 Excel 一致</strong><span>白色 = 可录入 / 覆盖</span><span>灰色 = 计算结果</span></div><div><span class="legend-dot ok"></span> 已记录 <span class="legend-dot warn"></span> 业务待确认</div></div><div class="table-scroll"><table class="ullage-table">' + head + body + '</table></div><div class="excel-footnotes"><p><strong>(1) G.H.L.</strong> Gauge Hatch Location：F = Forward（前），C = Center（中），A = Aft（后）。</p><p><strong>(2) I/U</strong> Innage / Ullage：I = 实高，U = 空距。</p><p><strong>TRACE</strong> 原表 5C 的 Interface 为微量痕迹、Volume 为 0；这是原始状态，不等同于“未测量”。</p></div></div>';
    }
    function renderFreeWater() {
      const t = totals();
      const head = '<thead><tr><th rowSpan="2">Tank No.<small>舱号</small></th><th colSpan="2">Current Ullage Result<small>当前抵港计量结果</small></th><th colSpan="2">Detected by UTI<small>UTI 检测</small></th><th colSpan="2">Water Finding Paste<small>试水膏检测</small></th><th rowSpan="2">Bottom Sample<small>底部样可见游离水</small></th><th rowSpan="2">Determination Method<small>最终判定方法</small></th><th colSpan="2">Final Determination<small>最终结果 / 自动回写</small></th><th rowSpan="2">Status<small>状态</small></th></tr>' +
        '<tr><th>Interface<small>水界面 · m</small></th><th>Volume<small>体积 · m³</small></th><th>Gauge<small>水高 · m</small></th><th>Volume<small>体积 · m³</small></th><th>Gauge<small>水高 · m</small></th><th>Volume<small>体积 · m³</small></th><th>Gauge<small>水高 · m</small></th><th>Volume<small>体积 · m³</small></th></tr></thead>';
      const body = '<tbody>' + cargoTanks.map(r => {
        const sel = r.id === selectedCalculationId; const det = r.fwSource === "DETERMINATION";
        return '<tr' + (sel ? ' class="selected-fw-row"' : '') + '>' +
          '<th><button type="button" aria-pressed="' + sel + '" onclick="selectedCalculationId=' + r.id + ';renderFreeWater()">' + r.tank + '<small>' + (sel ? "当前编辑" : "选择此舱") + '</small></button></th>' +
          '<td class="imported-fw-value">' + (r.fwInterface === "" ? "—" : r.fwInterface) + '</td><td class="imported-fw-value number">' + fmt(r.freeWater, 2) + '</td>' +
          '<td><input aria-label="' + r.tank + ' UTI 水高" value="' + (r.utiGauge ?? "") + '" placeholder="数值/TRACE" onchange="updFW(' + r.id + ',`utiGauge`,this.value)"></td>' +
          '<td><input aria-label="' + r.tank + ' UTI 水体积" type="number" min="0" step="0.01" value="' + (r.utiVolume ?? "") + '" onchange="updFW(' + r.id + ',`utiVolume`,this.value)"></td>' +
          '<td><input aria-label="' + r.tank + ' 试水膏水高" value="' + (r.pasteGauge ?? "") + '" placeholder="数值/TRACE" onchange="updFW(' + r.id + ',`pasteGauge`,this.value)"></td>' +
          '<td><input aria-label="' + r.tank + ' 试水膏水体积" type="number" min="0" step="0.01" value="' + (r.pasteVolume ?? "") + '" onchange="updFW(' + r.id + ',`pasteVolume`,this.value)"></td>' +
          '<td><select aria-label="' + r.tank + ' 底部样" onchange="updFW(' + r.id + ',`bottomSampleVisible`,this.value)"><option value="">待选择</option><option value="YES"' + (r.bottomSampleVisible === "YES" ? " selected" : "") + '>Yes · 是</option><option value="NO"' + (r.bottomSampleVisible === "NO" ? " selected" : "") + '>No · 否</option></select></td>' +
          '<td><select aria-label="' + r.tank + ' 判定方法" onchange="updFW(' + r.id + ',`determinationMethod`,this.value)"><option value="">待选择</option><option value="UTI"' + (r.determinationMethod === "UTI" ? " selected" : "") + '>UTI</option><option value="PASTE"' + (r.determinationMethod === "PASTE" ? " selected" : "") + '>Water Finding Paste</option><option value="AVERAGE"' + (r.determinationMethod === "AVERAGE" ? " selected" : "") + '>Average</option></select></td>' +
          '<td class="final-fw-value">' + (det ? r.fwInterface : "—") + '<small>' + (det ? "已回写" : "等待判定") + '</small></td><td class="final-fw-value number">' + (det ? fmt(r.freeWater, 2) : "—") + '<small>' + (det ? "参与 GOV" : "未替换导入值") + '</small></td>' +
          '<td><span class="status-pill ' + (det ? "success" : "warning") + '">' + (det ? "已判定" : "待补依据") + '</span></td></tr>';
      }).join('') +
        '<tfoot><tr><th colSpan="2">FINAL TOTAL · 最终合计</th><td>' + fmt(t.fw, 2) + '</td><td colSpan="6">完成判定后，同一条记录直接更新抵港主表，不产生第二份 FW 数据</td><td colSpan="2">' + cargoTanks.filter(r => r.fwSource === "DETERMINATION").length + ' / ' + cargoTanks.length + ' 已联动</td><td>m³</td></tr></tfoot>';
      document.getElementById("panel-freeWater").innerHTML =
        '<section class="free-water-lineage"><div><span>01</span><p><strong>UTI Measurement</strong><small>UTI 水高与体积</small></p></div><b>+</b><div><span>02</span><p><strong>Water Finding Paste</strong><small>试水膏水高与体积</small></p></div><b>+</b><div><span>03</span><p><strong>Bottom Sample</strong><small>底部样观察</small></p></div><b>→</b><div><span>04</span><p><strong>Final Determination</strong><small>最终 FW Interface / Volume</small></p></div><b>→</b><div class="lineage-result"><span>05</span><p><strong>Ullage Calculation</strong><small>回写主表并重算 GOV / GSV</small></p></div></section>' +
        '<div class="free-water-import-warning"><strong>数据迁移说明 / Migration Notice</strong><span>当前 Ullage 的最终 FW 结果已保留，但 Excel「Vsl FW」中的检测明细属于不同日期/批次且数值不一致，因此未自动导入。补录并完成判定后，系统才会把来源切换为“游离水测定”。</span></div>' +
        '<section class="free-water-context"><header><div><p class="eyebrow">MEASUREMENT CONTEXT · 测定条件</p><h3>Free Water Measurement Report</h3></div><span class="source-badge project">与抵港计量共用项目快照</span></header><div><dl><dt>UTI SER. NO.<small>UTI 仪器编号</small></dt><dd>' + conditions.utiSerialNo + '</dd></dl><dl><dt>WATER FINDING PASTE<small>试水膏品牌</small></dt><dd>' + conditions.waterPasteBrand + '</dd></dl><dl><dt>DETECTED BY<small>检测方式</small></dt><dd>' + conditions.fwDetectedBy + '</dd></dl><dl><dt>DATE / TIME<small>测定日期时间</small></dt><dd>' + conditions.inspectionDate + ' · ' + conditions.inspectionTime + '</dd></dl></div></section>' +
        '<div class="metric-row free-water-metrics">' +
        '<article><span>Tank Records · 舱位记录</span><strong>' + cargoTanks.length + '</strong><small>与抵港船舱清单共用</small></article>' +
        '<article><span>Determined · 已完成判定</span><strong>' + cargoTanks.filter(r => r.fwSource === "DETERMINATION").length + '</strong><small>完成后自动回写主表</small></article>' +
        '<article><span>Imported Result · 仅有导入结果</span><strong>' + cargoTanks.filter(r => r.fwSource !== "DETERMINATION").length + '</strong><small>缺少 UTI / 试水膏明细</small></article>' +
        '<article class="metric-accent"><span>Final FW Volume · 最终游离水</span><strong>' + fmt(t.fw, 2) + '</strong><small>m³ · 参与 GOV 计算</small></article></div>' +
        '<section class="table-card free-water-table-card"><div class="table-toolbar"><div><strong>逐舱测定记录</strong><span>最终结果只由选定的判定方法生成</span></div><div><span class="legend-dot ok"></span> 已联动 <span class="legend-dot warn"></span> 待补测定依据</div></div><div class="table-scroll"><table class="free-water-table">' + head + body + '</table></div><div class="free-water-rule-note" style="padding:10px 13px;font-size:10px;color:var(--text-secondary)"><strong>客户指示 / Client Instruction</strong><span>Excel 示例说明：底部样可见游离水时报告 UTI 结果，否则采用 UTI 与试水膏的平均值；但示例行存在不完全一致的选择，因此原型保留人工选择并要求后续由业务人员确认自动化规则。</span></div></section>';
    }
    function renderCalculation() {
      const t = totals();
      const rowsHtml = rows.map(r => {
        const gov = Math.max(r.tov - r.freeWater, 0); const sel = r.id === selectedCalculationId;
        return '<tr' + (sel ? ' class="selected-calculation-row"' : '') + '>' +
          '<th><button type="button" aria-pressed="' + sel + '" onclick="selectedCalculationId=' + r.id + ';renderCalculation()">' + r.tank + '<small>' + (r.assetType === "PIPELINE" ? "Pipeline · 管线" : "View trace · 查看追溯") + '</small></button></th>' +
          '<td class="input-value">' + r.corrected.toFixed(3) + '</td><td class="input-value">' + (r.temperature === "" ? "—" : r.temperature.toFixed(1)) + '</td>' +
          '<td class="input-value">' + fmt(r.tov, 2) + '</td><td class="input-value">' + fmt(r.freeWater, 2) + '</td>' +
          '<td class="formula-value">' + fmt(gov, 2) + '<small>= ' + fmt(r.tov, 2) + ' − ' + fmt(r.freeWater, 2) + '</small></td>' +
          '<td class="formula-value">' + r.vcf.toFixed(5) + '<small>T-54A · ' + vcfVersion + '</small></td>' +
          '<td class="formula-value strong">' + fmt(gov * r.vcf, 3) + '<small>= GOV × VCF</small></td>' +
          '<td><span class="status-pill ' + (r.assetType === "PIPELINE" ? "neutral" : "success") + '">' + (r.assetType === "PIPELINE" ? "管线记录" : "公式已复核") + '</span></td></tr>';
      }).join('') +
        '<tfoot><tr><th colSpan="3">TOTAL · 合计</th><td>' + fmt(t.tov, 2) + '</td><td>' + fmt(t.fw, 2) + '</td><td>' + fmt(t.gov, 2) + '</td><td>—</td><td>' + fmt(t.gsv, 3) + '</td><td>17 舱 + P.Line</td></tr></tfoot>';
      const qHtml = quantityConversions.map(it => {
        const gross = t.gsv * it.factor; const net = gross * netFactor;
        return '<tr><th>' + it.label + '<small>' + it.zh + '</small></th><td class="number">' + it.factor.toFixed(it.factor === 1 ? 0 : 9) + '</td><td class="number">' + fmt(gross, it.digits) + '</td><td class="number">− ' + fmt(gross - net, it.digits) + '</td><td class="number strong">' + fmt(net, it.digits) + '</td></tr>';
      }).join('');
      document.getElementById("panel-calculation").innerHTML =
        '<section class="calculation-lineage" aria-label="数据录入与计算明细关系"><div><span class="lineage-index">01</span><p><strong>Data Entry</strong><small>数据录入：Gauge、温度、TOV、FW</small></p></div><b>→</b><div><span class="lineage-index">02</span><p><strong>Per-tank Calculation</strong><small>逐舱计算：GOV、VCF、GSV</small></p></div><b>→</b><div><span class="lineage-index">03</span><p><strong>Quantity Conversion</strong><small>汇总换算：标准体积、重量、毛量/净量</small></p></div><b>→</b><div><span class="lineage-index">04</span><p><strong>Report Output</strong><small>报告输出：Ullage Report / Quantity</small></p></div></section>' +
        '<div class="calculation-source-guide"><span><i class="calc-source input"></i>Data Entry · 数据录入值</span><span><i class="calc-source parameter"></i>Project Parameter · 项目参数</span><span><i class="calc-source formula"></i>Excel Formula · 已确认公式</span><span><i class="calc-source pending"></i>Business Rule · 待业务确认</span></div>' +
        '<section class="calculation-basis"><header><div><p class="eyebrow">CALCULATION BASIS · 计算依据</p><h3>当前项目参数与 Excel 口径</h3></div><span>来源：Ullage 页 105–110、133–148 行</span></header><div>' +
        '<dl><dt>VCF TABLE<small>VCF 表号</small></dt><dd>T-54A</dd><em class="calc-chip parameter">项目参数</em></dl>' +
        '<dl><dt>VCF VERSION<small>VCF 版本</small></dt><dd>' + vcfVersion + '</dd><em class="calc-chip parameter">项目参数</em></dl>' +
        '<dl><dt>DENSITY @20℃<small>20℃ 密度</small></dt><dd>' + conditions.densityAt20.toFixed(4) + ' g/cm³</dd><em class="calc-chip input">报告输入</em></dl>' +
        '<dl><dt>STANDARD DENSITY @15℃<small>15℃ 标准密度</small></dt><dd>' + excelStandardDensity15.toFixed(1) + ' kg/m³</dd><em class="calc-chip formula">Excel 结果</em></dl>' +
        '<dl><dt>WCF MT (AIR)<small>空气中公吨换算系数</small></dt><dd>' + excelWcfMtAir.toFixed(9) + '</dd><em class="calc-chip formula">Excel 结果</em></dl>' +
        '<dl class="basis-warning"><dt>S&W % V/V<small>沉淀物和水体积百分比</small></dt><dd>' + excelSandWaterPct.toFixed(3) + '%</dd><em class="calc-chip pending">项目设置为 ' + conditions === "" ? "" : "已记录" + '%</em></dl></div></section>' +
        '<section class="calculation-detail-card"><header><div><p class="eyebrow">PER-TANK CALCULATION · 逐舱计算</p><h3>Excel 公式链与逐舱结果</h3></div><p>点击舱号查看该舱完整追溯链</p></header><div class="table-scroll"><table class="calculation-detail-table"><thead><tr><th>Tank No.<small>舱号</small></th><th>Corr\'d<small>修正液位 · m</small></th><th>Temp.<small>温度 · ℃</small></th><th>TOV<small>总观测体积 · m³</small></th><th>FW Volume<small>游离水体积 · m³</small></th><th>GOV<small>TOV − FW · m³</small></th><th>VCF<small>vcf(...) 自定义函数</small></th><th>GSV<small>ROUND(GOV × VCF, 3)</small></th><th>Rule Status<small>规则状态</small></th></tr></thead><tbody>' + rowsHtml + '</tbody></table></div></section>' +
        '<section class="quantity-conversion-card"><header><div><p class="eyebrow">TOTAL QUANTITY · 数量汇总</p><h3>Excel 表尾毛量、净量及单位换算</h3></div><p>Net = Gross × (1 − S&W%)</p></header><div class="quantity-summary-strip"><dl><dt>Gross Standard Volume<small>标准毛体积</small></dt><dd>' + fmt(t.gsv, 3) + ' m³</dd></dl><b>→</b><dl><dt>Total Free Water Volume<small>游离水总体积</small></dt><dd>' + fmt(t.fw, 2) + ' m³</dd></dl><b>=</b><dl><dt>Total Calculated Volume<small>总计算体积</small></dt><dd>' + fmt(t.gsv + t.fw, 3) + ' m³</dd></dl></div><div class="table-scroll"><table><thead><tr><th>Quantity Unit<small>数量单位</small></th><th>Conversion Factor<small>换算系数</small></th><th>Gross<small>毛量</small></th><th>S&W Deduction<small>沉淀物和水扣除</small></th><th>Net<small>净量</small></th></tr></thead><tbody>' + qHtml + '</tbody></table></div><div class="calculation-discrepancy"><strong>口径提示 / Basis Warning</strong><span>Excel Ullage 表尾的 S&W 为 ' + excelSandWaterPct.toFixed(3) + '%，而当前“项目与报告设置”为 ' + (document.getElementById("sedimentWaterPct") ? document.getElementById("sedimentWaterPct").value : "0.12") + '%。两者未确认前，正式软件不能静默选择其中一个。</span></div></section>';
    }
    function renderIssues() {
      document.getElementById("panel-issues").innerHTML =
        '<div class="issues-list" aria-live="polite">' +
        '<article><span class="issue-code">B-001</span><div><h3>Corr\'d 的生成逻辑尚未从 Excel 公式中确认</h3><p>字段已经按原表恢复，但需要业务人员确认它是人工录入，还是由 Obs\'d、Trim、List 和舱容表自动修正。</p></div><button type="button" onclick="switchPanel(\'entry\')">查看字段</button></article>' +
        '<article><span class="issue-code">B-002</span><div><h3>5C 的 TRACE 需要确认报告规则</h3><p>原表 Interface 显示 TRACE、FW Volume 为 0。需确认软件中是否允许直接选“TRACE”，以及打印时是否必须保持英文。</p></div><button type="button" onclick="switchPanel(\'entry\')">定位数据表</button></article>' +
        '<article><span class="issue-code">B-003</span><div><h3>项目设置与 Ullage 表尾的 S&W 数值不一致</h3><p>项目设置当前为 ' + (document.getElementById("sedimentWaterPct") ? document.getElementById("sedimentWaterPct").value : "0.12") + '%，Excel Ullage 表尾为 0.025%。需要确认最终净量计算采用哪个来源，以及是否允许项目级覆盖。</p></div><button type="button" onclick="switchPanel(\'calculation\')">查看数量换算</button></article>' +
        '</div>';
    }
    renderConditions(); renderMetrics(); renderEntry(); renderFreeWater(); renderCalculation(); renderIssues();
"""
    return body, js


# ---------------- STEP 04 ----------------
def step04():
    body = r"""
          <div class="workspace-heading shore-heading">
            <div><p class="eyebrow">STEP 04 · EXCEL SHEETS「SHORE TK / SHORE TK (2)」</p><h2>Shore Tank Measurement <small>岸罐接收计量</small></h2><p>按 Excel 原结构恢复两张岸罐页、六组 Open / Close 位置、现场输入、岸罐主数据、修正公式和多单位输出。</p></div>
            <div class="context-actions"><span class="excel-fidelity-badge">Excel 字段完整映射</span><button type="button" class="button tertiary" onclick="alert('（演示）岸罐基础资料')">岸罐基础资料</button><button type="button" class="button tertiary" onclick="alert('（演示）罐容表版本')">罐容表版本</button></div>
          </div>
          <section class="shore-context-card">
            <header><div><p class="eyebrow">REPORT CONTEXT · 报告条件</p><h3>SHORE TANK MEASUREMENT REPORT</h3></div><span class="source-badge project">项目快照 + 岸罐主数据</span></header>
            <div class="shore-context-grid" id="shoreContext"></div>
          </section>
          <div class="metric-row shore-metrics" id="shoreMetrics" aria-label="岸罐计量汇总"></div>
          <div class="tabbar" role="tablist" aria-label="岸罐工作区视图">
            <button type="button" role="tab" aria-selected="true" data-panel="entry" onclick="switchShore('entry')">Open / Close Entry <small>原表数据录入</small></button>
            <button type="button" role="tab" aria-selected="false" data-panel="calculation" onclick="switchShore('calculation')">Calculation Details <small>计算明细</small></button>
            <button type="button" role="tab" aria-selected="false" data-panel="output" onclick="switchShore('output')">Quantity Output <small>多单位数量输出</small></button>
            <button type="button" role="tab" aria-selected="false" data-panel="issues" onclick="switchShore('issues')">Validation Issues <small>校验问题</small></button>
            <button type="button" class="validate-action" onclick="alert('（演示）运行校验：4 项问题')">Run Validation <small>运行校验</small></button>
          </div>
          <div id="shore-entry"></div>
          <div id="shore-calculation" hidden></div>
          <div id="shore-output" hidden></div>
          <div id="shore-issues" hidden></div>
          <footer class="workspace-footer">
            <div><strong>下一步：卸货后 ROB</strong><span>本机草稿会保留各步骤录入状态，可随时返回修改</span></div>
            <a class="button primary" href="step-05-rob.html">保存并进入下一步</a>
          </footer>
"""
    js = (
        COMMON_SHORE_JS()
    )
    return body, js


# ---------------- STEP 05 ----------------
def step05():
    body = r"""
          <div class="workspace-heading">
            <div><p class="eyebrow">步骤 05</p><h2>卸货后 ROB</h2><p>逐舱记录液态与非液态残留、可泵状态和现场说明，计算离港剩余标准体积。</p></div>
            <div class="context-actions"><button type="button" class="button tertiary" onclick="alert('（演示）离港条件')">离港条件</button><button type="button" class="button secondary" onclick="alert('（演示）批量标记空舱')">批量标记空舱</button></div>
          </div>
          <div class="metric-row" id="robMetrics" aria-label="ROB 汇总"></div>
          <div class="tabbar" role="tablist" aria-label="ROB 工作区视图">
            <button type="button" role="tab" aria-selected="true" data-panel="entry" onclick="switchRob('entry')">逐舱记录</button>
            <button type="button" role="tab" aria-selected="false" data-panel="calculation" onclick="switchRob('calculation')">计算明细</button>
            <button type="button" role="tab" aria-selected="false" data-panel="issues" onclick="switchRob('issues')">校验问题</button>
          </div>
          <div id="rob-entry"></div>
          <div id="rob-calculation" hidden></div>
          <div id="rob-issues" hidden></div>
          <footer class="workspace-footer">
            <div><strong>下一步：VEF 经验系数</strong><span>本机草稿会保留各步骤录入状态，可随时返回修改</span></div>
            <a class="button primary" href="step-06-vef.html">保存并进入下一步</a>
          </footer>
"""
    js = r"""
    const rows = [
      { id: 1, tank: "1C", status: "LIQUID", liquidVolume: 42.8, nonLiquidVolume: 0, pumpable: false, temperature: 18.2, vcf: 0.99734, note: "舱底残液，不可继续泵出" },
      { id: 2, tank: "2C", status: "LIQUID", liquidVolume: 31.4, nonLiquidVolume: 0, pumpable: false, temperature: 18.1, vcf: 0.99743, note: "" },
      { id: 3, tank: "3C", status: "EMPTY", liquidVolume: 0, nonLiquidVolume: 0, pumpable: false, temperature: 18.0, vcf: 0.99752, note: "干舱" },
      { id: 4, tank: "4C", status: "LIQUID", liquidVolume: 58.6, nonLiquidVolume: 0, pumpable: false, temperature: 18.3, vcf: 0.99726, note: "" },
      { id: 5, tank: "5C", status: "NON_LIQUID", liquidVolume: 0, nonLiquidVolume: 12.5, pumpable: false, temperature: 18.1, vcf: 0.99743, note: "舱底非液态残留" },
      { id: 6, tank: "1P", status: "LIQUID", liquidVolume: 27.9, nonLiquidVolume: 0, pumpable: true, temperature: 18.0, vcf: 0.99752, note: "等待最终扫舱确认" },
      { id: 7, tank: "1S", status: "EMPTY", liquidVolume: 0, nonLiquidVolume: 0, pumpable: false, temperature: 18.0, vcf: 0.99752, note: "干舱" },
      { id: 8, tank: "2P", status: "LIQUID", liquidVolume: 35.2, nonLiquidVolume: 0, pumpable: false, temperature: 18.2, vcf: 0.99734, note: "" }
    ];
    function robTotals() { return rows.reduce((s, r) => s + r.liquidVolume * r.vcf + r.nonLiquidVolume, 0); }
    function updRob(id, field, val) { const r = rows.find(x => x.id === id); if (!r) return; if (field === "status") r.status = val; else if (field === "pumpable") r.pumpable = val; else r[field] = Number(val); renderRobEntry(); renderRobMetrics(); }
    function switchRob(p) { ["entry", "calculation", "issues"].forEach(x => { document.getElementById("rob-" + x).hidden = x !== p; }); document.querySelectorAll(".tabbar button[data-panel]").forEach(b => b.setAttribute("aria-selected", b.dataset.panel === p ? "true" : "false")); }
    function renderRobMetrics() {
      const liquidTotal = rows.reduce((s, r) => s + r.liquidVolume, 0);
      const nonLiquidTotal = rows.reduce((s, r) => s + r.nonLiquidVolume, 0);
      const pumpableCount = rows.filter(r => r.pumpable && r.liquidVolume > 0).length;
      document.getElementById("robMetrics").innerHTML =
        '<article><span>已检查舱位</span><strong>' + rows.length + ' / 17</strong><small>' + (17 - rows.length) + ' 个待检查</small></article>' +
        '<article><span>液态残留</span><strong>' + fmt(liquidTotal, 2) + '</strong><small>m³ · 观测体积</small></article>' +
        '<article><span>非液态残留</span><strong>' + fmt(nonLiquidTotal, 2) + '</strong><small>m³ · 现场估算</small></article>' +
        '<article class="metric-accent"><span>ROB 标准体积</span><strong>' + fmt(robTotals(), 2) + '</strong><small>m³ @15℃</small></article>';
    }
    function renderRobEntry() {
      const totalGsv = robTotals();
      const body = '<tbody>' + rows.map(r => {
        const gsv = r.liquidVolume * r.vcf + r.nonLiquidVolume;
        const needsReview = r.pumpable && r.