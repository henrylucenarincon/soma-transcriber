/* Soma Studio — frontend logic */
'use strict';

// ── State ───────────────────────────────────────────────────────────────────
let isRunning = false;

// ── Study Pack Progress ───────────────────────────────────────────────────────
const PHASES = [
  { key: 'video-notes',      label: 'Video-notes',      signals: ['generando video-notes', 'video-note:'],       start: 2,  end: 40 },
  { key: 'module-summaries', label: 'Module-summaries',  signals: ['generando module-notes', 'module summary'],   start: 40, end: 62 },
  { key: 'evidence',         label: 'Evidence',          signals: ['generando evidencia', 'evidence::'],          start: 62, end: 82 },
  { key: 'course-pack',      label: 'Course-pack',       signals: ['generando course-pack', 'course-pack:'],      start: 82, end: 98 },
];

let progress = { active: false, phase: -1, pct: 0, total: 0, current: 0 };

function resetProgress(show = false) {
  progress = { active: show, phase: -1, pct: 0, total: 0, current: 0 };
  setProgressPct(0);
  document.getElementById('progressPhase').textContent = 'Iniciando…';
  document.getElementById('progressPct').textContent = '0%';
  document.getElementById('progressSection').classList.toggle('hidden', !show);
  PHASES.forEach(p => {
    const el = document.getElementById(`step-${p.key}`);
    if (el) { el.className = 'step'; el.textContent = `○ ${p.label}`; }
  });
}

function setProgressPct(pct) {
  pct = Math.min(100, Math.max(0, Math.round(pct)));
  document.getElementById('progressFill').style.width = pct + '%';
  document.getElementById('progressPct').textContent = pct + '%';
}

function parseProgressFromLine(line) {
  if (!progress.active) return;

  const low = line.toLowerCase();

  // Detect phase transitions
  PHASES.forEach((phase, i) => {
    if (phase.signals.some(s => low.includes(s))) {
      if (progress.phase < i) {
        // Mark previous phases done
        for (let j = 0; j < i; j++) {
          const el = document.getElementById(`step-${PHASES[j].key}`);
          if (el) { el.className = 'step done'; el.textContent = `✓ ${PHASES[j].label}`; }
        }
        // Mark current phase active
        progress.phase = i;
        progress.current = 0;
        const el = document.getElementById(`step-${phase.key}`);
        if (el) { el.className = 'step active'; el.textContent = `◉ ${phase.label}`; }
        document.getElementById('progressPhase').textContent = phase.label + '…';
        setProgressPct(phase.start);
      }
    }
  });

  // Parse tqdm-style N/M count from the line  e.g. "| 1/2 ["
  const nmMatch = line.match(/\|\s*(\d+)\/(\d+)\s*\[/);
  if (nmMatch && progress.phase >= 0) {
    const n = parseInt(nmMatch[1], 10);
    const m = parseInt(nmMatch[2], 10);
    if (m > 0) {
      const phase = PHASES[progress.phase];
      const within = (n / m) * (phase.end - phase.start);
      setProgressPct(phase.start + within);
    }
  }

  // Completion signals
  if (low.includes('study pack listo') || low.includes('[ok] proceso completado')) {
    PHASES.forEach(p => {
      const el = document.getElementById(`step-${p.key}`);
      if (el) { el.className = 'step done'; el.textContent = `✓ ${p.label}`; }
    });
    setProgressPct(100);
    document.getElementById('progressPhase').textContent = '¡Completado!';
    document.getElementById('progressPct').textContent = '100%';
  }
}

// ── Init ────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadConfigs();
  setupPhaseCards();
  onMaxVideosChange();
  switchTab('transcription');
  document.getElementById('outputPath').addEventListener('change', () => loadCourses());
  loadCourses();
  checkRunningJob(); // reconnect if a job was running before reload
});

// ── Job reconnection ──────────────────────────────────────────────────────────
async function checkRunningJob() {
  try {
    const res = await fetch('/api/jobs/current');
    const data = await res.json();

    if (!data.job_id) return; // nothing to reconnect

    const isStudyPack = data.type === 'study-pack';
    const isRunning   = data.running;

    // Switch to the right tab
    switchTab(isStudyPack ? 'study-pack' : 'transcription');

    clearLog();
    resetProgress(isStudyPack);
    setRunning(isRunning);

    const banner = isRunning
      ? '⟳ Reconectando al proceso en curso…\n'
      : '↺ Mostrando output del último proceso:\n';
    appendLog(banner);

    // Stream or replay the log
    try {
      const streamRes = await fetch(`/api/jobs/${data.job_id}/reconnect`);
      if (!streamRes.ok) { setRunning(false); return; }

      const reader  = streamRes.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;
        const lines = buffer.split('\n');
        buffer = lines.pop();
        if (isStudyPack) lines.forEach(l => parseProgressFromLine(l));
        appendLog(chunk);
      }
    } catch (_) {}

    setRunning(false);
  } catch (_) {}
}

// ── Config helpers ───────────────────────────────────────────────────────────
function getConfig() {
  // Course name: prefer hidden input (synced from both select and text modes)
  const courseNameFromSelect = (() => {
    const sel = document.getElementById('courseNameSelect');
    const val = sel?.value;
    return (val && val !== '__new__') ? val : '';
  })();
  const courseNameFromInput = v('courseName');
  const courseName = courseNameFromInput || courseNameFromSelect;

  return {
    coursePath:  v('coursePath'),
    outputPath:  v('outputPath') || './output',
    courseName,
    configPath:  v('configPath') || null,
    maxVideos:   parseInt(v('maxVideos'), 10) || null,
    force:       document.getElementById('forceCheck').checked,
  };
}

function getStudyConfig() {
  const base = getConfig();
  const phase = document.querySelector('input[name="phase"]:checked')?.value || 'all';
  const module = document.getElementById('moduleFilter')?.value || null;
  return { ...base, phase, module };
}

function v(id) {
  return (document.getElementById(id)?.value || '').trim();
}

function isReady() {
  const c = getConfig();
  return c.coursePath && c.courseName && c.outputPath;
}

function onConfigChange() { /* reserved for future reactivity */ }

function onMaxVideosChange() {
  const val = parseInt(v('maxVideos'), 10);
  const chip = document.getElementById('maxVideosChip');
  const warn = document.getElementById('maxVideosWarn');

  if (isNaN(val) || val === 1) {
    chip.textContent = 'Prueba';
    chip.className = 'chip chip-success';
    warn.classList.add('hidden');
  } else if (val === 0) {
    chip.textContent = 'Sin límite';
    chip.className = 'chip chip-warn';
    warn.classList.remove('hidden');
  } else {
    chip.textContent = `${val} videos`;
    chip.className = 'chip chip-info';
    warn.classList.add('hidden');
  }
}

// ── Modules ───────────────────────────────────────────────────────────────────
async function loadModules(courseName) {
  const outputPath = v('outputPath') || './output';
  const select = document.getElementById('moduleFilter');
  if (!select) return;

  select.innerHTML = '<option value="">Todos los módulos</option>';
  if (!courseName) return;

  try {
    const res = await fetch(`/api/modules?output=${encodeURIComponent(outputPath)}&course_name=${encodeURIComponent(courseName)}`);
    const data = await res.json();
    (data.modules || []).forEach(mod => {
      const opt = document.createElement('option');
      opt.value = mod;
      opt.textContent = mod;
      select.appendChild(opt);
    });
  } catch (_) {}
}

function onModuleChange() { /* reactive hook for future use */ }

// ── Existing courses ──────────────────────────────────────────────────────────
async function loadCourses() {
  const outputPath = v('outputPath') || './output';
  try {
    const res = await fetch(`/api/courses?output=${encodeURIComponent(outputPath)}`);
    const data = await res.json();
    const courses = data.courses || [];
    const selectRow = document.getElementById('courseNameSelectRow');
    const inputRow  = document.getElementById('courseNameInputRow');
    const select    = document.getElementById('courseNameSelect');
    const backBtn   = document.getElementById('backToSelectBtn');

    if (courses.length === 0) {
      // No existing courses — show plain input
      selectRow.classList.add('hidden');
      inputRow.classList.remove('hidden');
      backBtn.classList.add('hidden');
      return;
    }

    // Populate dropdown
    const currentName = v('courseName');
    select.innerHTML = '<option value="">Selecciona un curso...</option>';
    courses.forEach(name => {
      const opt = document.createElement('option');
      opt.value = name;
      opt.textContent = name;
      if (name === currentName) opt.selected = true;
      select.appendChild(opt);
    });

    // Add "Nuevo curso..." at the end
    const newOpt = document.createElement('option');
    newOpt.value = '__new__';
    newOpt.textContent = '+ Nuevo curso...';
    select.appendChild(newOpt);

    // Show select, hide text input (unless user was already in new-course mode)
    const isNewMode = inputRow.classList.contains('new-mode');
    if (!isNewMode) {
      selectRow.classList.remove('hidden');
      inputRow.classList.add('hidden');
      backBtn.classList.add('hidden');
      // Auto-select if there's only one course
      if (courses.length === 1 && !currentName) {
        select.value = courses[0];
        document.getElementById('courseName').value = courses[0];
        loadModules(courses[0]);
      }
    }
  } catch (_) {}
}

function onCourseSelectChange() {
  const select = document.getElementById('courseNameSelect');
  const val = select.value;

  if (val === '__new__') {
    showNewCourse();
    return;
  }

  document.getElementById('courseName').value = val;
  loadModules(val);
}

function showNewCourse() {
  const selectRow = document.getElementById('courseNameSelectRow');
  const inputRow  = document.getElementById('courseNameInputRow');
  const backBtn   = document.getElementById('backToSelectBtn');
  const input     = document.getElementById('courseName');

  selectRow.classList.add('hidden');
  inputRow.classList.remove('hidden');
  inputRow.classList.add('new-mode');
  backBtn.classList.remove('hidden');
  input.value = '';
  input.focus();
}

function showCourseSelect() {
  const selectRow = document.getElementById('courseNameSelectRow');
  const inputRow  = document.getElementById('courseNameInputRow');
  const backBtn   = document.getElementById('backToSelectBtn');
  const select    = document.getElementById('courseNameSelect');

  selectRow.classList.remove('hidden');
  inputRow.classList.add('hidden');
  inputRow.classList.remove('new-mode');
  backBtn.classList.add('hidden');

  // Sync text input with dropdown value
  const val = select.value;
  if (val && val !== '__new__') {
    document.getElementById('courseName').value = val;
  }
}

// ── Config files ─────────────────────────────────────────────────────────────
async function loadConfigs() {
  try {
    const res = await fetch('/api/configs');
    const data = await res.json();
    const select = document.getElementById('configPath');
    select.innerHTML = '<option value="">Sin perfil</option>';
    (data.configs || []).forEach(cfg => {
      const opt = document.createElement('option');
      opt.value = cfg;
      opt.textContent = cfg;
      select.appendChild(opt);
    });
  } catch (_) {}
}

// ── Folder picker ─────────────────────────────────────────────────────────────
async function pickFolder(field) {
  const titles = {
    course: 'Selecciona la carpeta del curso',
    output: 'Selecciona la carpeta de output',
  };
  try {
    const res = await fetch('/api/select-folder', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: titles[field] || 'Selecciona una carpeta' }),
    });
    const data = await res.json();
    if (data.path) {
      const ids = { course: 'coursePath', output: 'outputPath' };
      const el = document.getElementById(ids[field]);
      if (el) {
        el.value = data.path;
        el.dispatchEvent(new Event('input'));
      }
    }
  } catch (e) {
    appendLog(`Error al abrir selector: ${e.message}\n`);
  }
}

// ── Tab navigation ────────────────────────────────────────────────────────────
function switchTab(name) {
  document.querySelectorAll('.tab').forEach(t => {
    t.classList.toggle('active', t.dataset.tab === name);
  });
  document.querySelectorAll('.tab-content').forEach(c => {
    c.classList.toggle('hidden', c.id !== `tab-${name}`);
  });
  if (name === 'status') loadStatus();
}

// ── Phase cards ────────────────────────────────────────────────────────────────
function setupPhaseCards() {
  document.querySelectorAll('.phase-card').forEach(card => {
    card.addEventListener('click', () => {
      document.querySelectorAll('.phase-card').forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
    });
  });
}

// ── Streaming ──────────────────────────────────────────────────────────────────
async function streamCommand(endpoint, body, { showProgress = false } = {}) {
  if (isRunning) return;
  clearLog();
  resetProgress(showProgress);
  setRunning(true);

  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      appendLog(`Error HTTP ${res.status}: ${await res.text()}\n`);
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value, { stream: true });
      buffer += chunk;

      // Process complete lines for progress parsing
      const lines = buffer.split('\n');
      buffer = lines.pop(); // keep incomplete last line
      lines.forEach(line => parseProgressFromLine(line));
      if (showProgress) parseProgressFromLine(chunk); // also parse raw chunk for tqdm

      appendLog(chunk);
    }
    // Process any remaining buffer
    if (buffer) parseProgressFromLine(buffer);

  } catch (e) {
    appendLog(`\nError de red: ${e.message}\n`);
  } finally {
    setRunning(false);
    // If progress was shown and didn't reach 100%, mark as finished
    if (showProgress && progress.active && progress.pct < 100) {
      setProgressPct(progress.pct < 10 ? progress.pct : 100);
    }
  }
}

// ── Transcription actions ──────────────────────────────────────────────────────
async function listVideos() {
  if (!isReady()) { alertConfig(); return; }
  const { coursePath, outputPath, courseName, configPath, maxVideos, force } = getConfig();

  clearLog();
  appendLog('Listando videos...\n');

  document.getElementById('videoListSection').classList.add('hidden');
  document.getElementById('videoListBody').innerHTML = '';

  setRunning(true);
  try {
    const res = await fetch('/api/list-videos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ course_path: coursePath, output_path: outputPath, course_name: courseName, config_path: configPath, max_videos: maxVideos, force }),
    });

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    const rows = [];
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value, { stream: true });
      appendLog(chunk);
      buffer += chunk;
    }

    // Parse lines like: "001. [completed] Módulo 01/video.ts"
    buffer.split('\n').forEach(line => {
      const m = line.match(/^\s*(\d+)\.\s+\[([^\]]+)\]\s+(.+?)\s*$/);
      if (m) rows.push({ index: m[1], status: m[2], path: m[3] });
    });

    if (rows.length > 0) {
      renderVideoList(rows);
    }
  } catch (e) {
    appendLog(`\nError: ${e.message}\n`);
  } finally {
    setRunning(false);
  }
}

function renderVideoList(rows) {
  const section = document.getElementById('videoListSection');
  const tbody = document.getElementById('videoListBody');
  const count = document.getElementById('videoListCount');

  count.textContent = `${rows.length} videos`;
  tbody.innerHTML = '';

  rows.forEach(({ index, status, path }) => {
    const tr = document.createElement('tr');
    const badgeClass = status === 'completed' ? 'badge-completed'
                     : status === 'failed'    ? 'badge-failed'
                     : status === 'processing'? 'badge-processing'
                     : 'badge-pending';
    tr.innerHTML = `
      <td style="color:var(--text-subtle);font-variant-numeric:tabular-nums">${index}</td>
      <td><span class="status-badge ${badgeClass}">${status}</span></td>
      <td style="font-family:var(--mono);font-size:11px" title="${path}">${path}</td>
    `;
    tbody.appendChild(tr);
  });

  section.classList.remove('hidden');
}

async function dryRun() {
  if (!isReady()) { alertConfig(); return; }
  const c = getConfig();
  await streamCommand('/api/dry-run', {
    course_path: c.coursePath, output_path: c.outputPath, course_name: c.courseName,
    config_path: c.configPath, max_videos: c.maxVideos, force: c.force,
  });
}

async function transcribe() {
  if (!isReady()) { alertConfig(); return; }
  const c = getConfig();

  if (!c.maxVideos && !confirm('¿Transcribir sin límite de videos? Esto puede generar costos de API significativos.')) return;

  await streamCommand('/api/transcribe', {
    course_path: c.coursePath, output_path: c.outputPath, course_name: c.courseName,
    config_path: c.configPath, max_videos: c.maxVideos, force: c.force,
  });
}

async function retryFailed() {
  if (!isReady()) { alertConfig(); return; }
  const c = getConfig();
  // Retry uses no max_videos limit and no force — processes pending/failed only
  await streamCommand('/api/transcribe', {
    course_path: c.coursePath, output_path: c.outputPath, course_name: c.courseName,
    config_path: c.configPath, max_videos: null, force: false,
  });
}

// ── Study Pack actions ─────────────────────────────────────────────────────────
async function studyPackDryRun() {
  if (!v('courseName')) { alertConfig(); return; }
  const c = getStudyConfig();
  await streamCommand('/api/study-pack/dry-run', {
    output_path: c.outputPath, course_name: c.courseName, config_path: c.configPath,
    max_videos: c.maxVideos, force: c.force, phase: c.phase, module: c.module || null,
  });
}

async function generateStudyPack() {
  if (!v('courseName')) { alertConfig(); return; }
  const c = getStudyConfig();

  const noLimit = !c.maxVideos && !c.module;
  if (noLimit && !confirm('¿Generar Study Pack completo sin límite de módulo ni videos? Esto puede generar costos significativos de API de Claude.')) return;

  await streamCommand('/api/study-pack/generate', {
    output_path: c.outputPath, course_name: c.courseName, config_path: c.configPath,
    max_videos: c.maxVideos, force: c.force, phase: c.phase, module: c.module || null,
  }, { showProgress: true });
}

// ── Status tab ─────────────────────────────────────────────────────────────────
async function loadStatus() {
  const container = document.getElementById('statusContent');
  container.innerHTML = '<div class="empty-state"><div class="empty-icon">◎</div><div>Cargando...</div></div>';

  try {
    const outputPath = v('outputPath') || './output';
    const courseName = v('courseName') || '';

    const [statusRes, indexRes] = await Promise.all([
      fetch(`/api/status?output=${encodeURIComponent(outputPath)}`),
      fetch(`/api/index?output=${encodeURIComponent(outputPath)}&course_name=${encodeURIComponent(courseName)}`),
    ]);

    const status = await statusRes.json();
    const index  = await indexRes.json();

    container.innerHTML = renderStatus(status, index);
  } catch (e) {
    container.innerHTML = `<div class="empty-state"><div class="empty-icon">✗</div><div>Error al cargar estado: ${e.message}</div></div>`;
  }
}

function renderStatus(status, index) {
  const manifest = status.manifest || {};
  const studyManifest = status.study_manifest || {};

  const completed = manifest.completed || 0;
  const failed    = manifest.failed    || 0;
  const pending   = manifest.pending   || 0;
  const processing= manifest.processing|| 0;

  const spCompleted = studyManifest.completed || 0;
  const spFailed    = studyManifest.failed    || 0;

  const files = [
    { label: 'manifest.json',       ok: status.manifest_exists },
    { label: 'study_manifest.json', ok: status.study_manifest_exists },
    { label: 'index.csv',           ok: status.index_exists },
  ];

  let html = `
    <div style="display:flex;flex-direction:column;gap:16px">

      <!-- Transcripción -->
      <div class="section">
        <div class="section-header">
          <span class="section-title">Transcripción (V1)</span>
        </div>
        <div class="section-body">
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-label">Completados</div>
              <div class="stat-value stat-completed">${completed}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">Fallidos</div>
              <div class="stat-value stat-failed">${failed}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">Pendientes</div>
              <div class="stat-value stat-pending">${pending + processing}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Study Pack -->
      <div class="section">
        <div class="section-header">
          <span class="section-title">Study Pack (V2)</span>
        </div>
        <div class="section-body">
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-label">Completados</div>
              <div class="stat-value stat-completed">${spCompleted}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">Fallidos</div>
              <div class="stat-value stat-failed">${spFailed}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Archivos -->
      <div class="section">
        <div class="section-header"><span class="section-title">Archivos</span></div>
        <div class="section-body">
          <div class="file-list">
            ${files.map(f => `
              <div class="file-item">
                <span class="${f.ok ? 'file-icon-ok' : 'file-icon-err'}">${f.ok ? '✓' : '✗'}</span>
                <span style="font-family:var(--mono);font-size:11px">${f.label}</span>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
  `;

  // Index table
  if (index.exists && index.rows && index.rows.length > 0) {
    const displayCols = ['course', 'module', 'video', 'status'].filter(c => index.columns.includes(c));
    html += `
      <div class="section">
        <div class="section-header">
          <span class="section-title">Index</span>
          <span class="chip chip-info">${index.rows.length} registros</span>
        </div>
        <div class="table-wrap" style="max-height:280px;overflow-y:auto">
          <table>
            <thead><tr>${displayCols.map(c => `<th>${c}</th>`).join('')}</tr></thead>
            <tbody>
              ${index.rows.slice(0, 200).map(row => `
                <tr>${displayCols.map(c => {
                  const val = row[c] || '';
                  if (c === 'status') {
                    const bc = val === 'completed' ? 'badge-completed' : val === 'failed' ? 'badge-failed' : 'badge-pending';
                    return `<td><span class="status-badge ${bc}">${val}</span></td>`;
                  }
                  return `<td>${val}</td>`;
                }).join('')}</tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  }

  html += '</div>';
  return html;
}

// ── Log ────────────────────────────────────────────────────────────────────────
function clearLog() {
  document.getElementById('logContent').innerHTML = '';
}

function appendLog(text) {
  const el = document.getElementById('logContent');

  // Split into lines and colorize
  const lines = text.split('\n');
  lines.forEach((line, i) => {
    if (i === lines.length - 1 && line === '') return; // skip trailing empty
    const span = document.createElement('span');
    span.textContent = (i < lines.length - 1) ? line + '\n' : line;

    const l = line.toLowerCase();
    if (l.includes('error') || l.includes('✗') || l.includes('failed')) {
      span.className = 'log-error';
    } else if (l.includes('[ok]') || l.includes('✓') || l.includes('completado') || l.includes('completed') || l.includes('listo')) {
      span.className = 'log-ok';
    } else if (l.includes('warning') || l.includes('skip') || l.includes('missing') || l.includes('warn')) {
      span.className = 'log-warning';
    } else if (l.includes('generando') || l.includes('procesando') || l.includes('process') || l.includes('generating')) {
      span.className = 'log-accent';
    } else if (l.startsWith('[') || l.includes('dry run')) {
      span.className = 'log-dim';
    }

    el.appendChild(span);
  });

  el.scrollTop = el.scrollHeight;
}

// ── Running state ──────────────────────────────────────────────────────────────
function setRunning(value) {
  isRunning = value;
  document.getElementById('runningDot').classList.toggle('hidden', !value);

  const btns = document.querySelectorAll('.btn');
  btns.forEach(btn => {
    if (!btn.id.startsWith('btn')) return;
    btn.disabled = value;
  });
}

// ── Helpers ────────────────────────────────────────────────────────────────────
function alertConfig() {
  appendLog('\nCompleta la configuración: Carpeta del curso, Nombre del curso y Output son obligatorios.\n');
}
