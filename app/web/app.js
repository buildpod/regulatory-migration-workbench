const state = { analysis: null, sources: [] };

const $ = (id) => document.getElementById(id);
const escapeHtml = (value) => String(value ?? '').replace(/[&<>'"]/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));

async function getJson(url, options = {}) {
  const response = await fetch(url, options);
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || `Request failed (${response.status})`);
  return body;
}

function renderSummary(analysis) {
  const highIssues = analysis.issues.filter((issue) => issue.severity === 'high').length;
  const stats = [
    ['Rows', analysis.row_count, 'records analysed'],
    ['Fields', analysis.column_count, 'columns profiled'],
    ['Issues', analysis.issues.length, `${highIssues} high severity`],
    ['Duplicate groups', analysis.duplicates.length, 'candidate groups'],
  ];
  $('summary').innerHTML = stats.map(([label, value, note]) => `<div class="stat-card"><div class="stat-value">${escapeHtml(value)}</div><div class="stat-label">${escapeHtml(label)}</div><div class="stat-note">${escapeHtml(note)}</div></div>`).join('');
}

function renderProfile(analysis) {
  $('profile-body').innerHTML = analysis.columns.map((column) => `<tr>
    <td><strong>${escapeHtml(column.name)}</strong></td>
    <td><span class="pill neutral">${escapeHtml(column.inferred_type)}</span></td>
    <td>${escapeHtml(column.blank_count)} <span class="muted">(${Math.round(column.blank_rate * 100)}%)</span></td>
    <td>${escapeHtml(column.unique_count)}</td>
    <td class="examples">${column.examples.map(escapeHtml).join(', ') || '—'}</td>
  </tr>`).join('');
}

function renderIssues(analysis) {
  $('issues').innerHTML = analysis.issues.length ? analysis.issues.map((issue) => `<article class="issue ${escapeHtml(issue.severity)}">
    <div class="issue-top"><span class="pill ${escapeHtml(issue.severity)}">${escapeHtml(issue.severity)}</span><strong>${escapeHtml(issue.issue_type)}</strong><span class="muted">${escapeHtml(issue.count)} record(s)</span></div>
    <p>${escapeHtml(issue.message)}</p>
    <small>${issue.rows ? `Rows: ${escapeHtml(issue.rows.join(', '))}` : `Field: ${escapeHtml(issue.field)}`}</small>
    <details><summary>Learn what this means</summary><p>${escapeHtml(issue.learning || 'Review the evidence with the data owner before deciding.')}</p><small>FAIR connection: ${escapeHtml(issue.fair_link || 'Review required')}</small></details>
  </article>`).join('') : '<p class="empty">No issues detected by the current rules.</p>';
}

function renderDuplicates(analysis) {
  $('duplicates').innerHTML = analysis.duplicates.length ? analysis.duplicates.map((group, index) => `<article class="duplicate-card">
    <div class="issue-top"><span class="pill ${group.kind === 'exact' ? 'high' : 'medium'}">${escapeHtml(group.kind)}</span><strong>Group ${index + 1}</strong></div>
    <p>${escapeHtml(group.match_reason)}</p><div class="row-list">Rows ${escapeHtml(group.row_numbers.join(', '))}</div>
    <div class="review-actions"><button class="mini-button" data-review="not-duplicate">Not duplicate</button><button class="mini-button" data-review="needs-review">Needs review</button><button class="mini-button" data-review="confirmed">Confirmed duplicate</button></div>
  </article>`).join('') : '<p class="empty">No duplicate candidates detected.</p>';
}

function renderFair(analysis) {
  $('fair').innerHTML = analysis.fair_assessment.map((item) => `<article class="fair-row">
    <div><strong>${escapeHtml(item.dimension)}</strong><p>${escapeHtml(item.evidence)}</p></div><span class="pill ${item.status === 'evidence-supported' ? 'low' : 'medium'}">${escapeHtml(item.status)}</span>
  </article>`).join('');
}

function renderSources(results = null) {
  const sourceMap = new Map((results || state.sources).map((item) => [item.id, item]));
  $('sources').innerHTML = state.sources.map((source) => {
    const result = sourceMap.get(source.id);
    const status = result?.status || 'not checked';
    return `<article class="source-row"><div><strong>${escapeHtml(source.name)}</strong><p>${escapeHtml(source.category)} · ${escapeHtml(source.jurisdiction)} · ${escapeHtml(source.mode)}</p><a href="${escapeHtml(source.url)}" target="_blank" rel="noreferrer">Open official source</a></div><span class="pill ${status === 'reachable' ? 'low' : status === 'unreachable' ? 'high' : 'neutral'}">${escapeHtml(status)}</span></article>`;
  }).join('');
}

async function analyse(filename, content) {
  $('upload-status').textContent = `Analysing ${filename}…`;
  try {
    state.analysis = await getJson('/api/analyse', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({filename, content})});
    renderSummary(state.analysis); renderProfile(state.analysis); renderIssues(state.analysis); renderDuplicates(state.analysis); renderFair(state.analysis);
    $('risk-decision').value = state.analysis.risk_decision.decision;
    $('risk-rationale').value = state.analysis.risk_decision.rationale;
    $('export-button').disabled = false;
    $('upload-status').textContent = `${filename}: ${state.analysis.row_count} row(s) analysed.`;
  } catch (error) { $('upload-status').textContent = error.message; }
}

$('file-input').addEventListener('change', (event) => {
  const file = event.target.files[0]; if (!file) return;
  const reader = new FileReader(); reader.onload = () => analyse(file.name, reader.result); reader.readAsText(file);
});

$('sample-button').addEventListener('click', async () => {
  try { const sample = await getJson('/api/sample'); await analyse(sample.filename, sample.content); } catch (error) { $('upload-status').textContent = error.message; }
});

$('health-button').addEventListener('click', async () => {
  $('health-button').disabled = true; $('health-button').textContent = 'Checking…';
  try { const result = await getJson('/api/source-health', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({})}); renderSources(result.results); }
  catch (error) { $('sources').insertAdjacentHTML('afterbegin', `<p class="callout error">${escapeHtml(error.message)}</p>`); }
  finally { $('health-button').disabled = false; $('health-button').textContent = 'Run health check'; }
});

$('risk-decision').addEventListener('change', () => { if (state.analysis) state.analysis.risk_decision.decision = $('risk-decision').value; });
$('risk-rationale').addEventListener('input', () => { if (state.analysis) state.analysis.risk_decision.rationale = $('risk-rationale').value; });

$('export-button').addEventListener('click', () => {
  if (!state.analysis) return;
  const blob = new Blob([JSON.stringify(state.analysis, null, 2)], {type: 'application/json'});
  const url = URL.createObjectURL(blob); const anchor = document.createElement('a'); anchor.href = url; anchor.download = 'migration-workbench-analysis.json'; anchor.click(); URL.revokeObjectURL(url);
});

fetch('/api/sources').then((response) => response.json()).then((body) => { state.sources = body.sources; renderSources(); }).catch((error) => { $('sources').innerHTML = `<p class="callout error">${escapeHtml(error.message)}</p>`; });

function renderLearning(learning) {
  $('quality-vs-fair').innerHTML = `<strong>${escapeHtml(learning.quality_vs_fair.title)}</strong><br>${escapeHtml(learning.quality_vs_fair.text)}`;
  $('fair-lessons').innerHTML = learning.fair_principles.map((lesson) => `<article class="lesson-card"><div class="lesson-letter">${escapeHtml(lesson.name[0])}</div><div><h3>${escapeHtml(lesson.name)}</h3><p class="question">${escapeHtml(lesson.question)}</p><p>${escapeHtml(lesson.plain_language)}</p><strong>Evidence to look for</strong><ul>${lesson.evidence.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul><p class="learn-connection">Cleanup connection: ${escapeHtml(lesson.cleanup_connection)}</p></div></article>`).join('');
  $('cleanup-steps').innerHTML = learning.cleanup_steps.map((step) => `<article class="step-card"><span class="step-number">${escapeHtml(step.number)}</span><div><h3>${escapeHtml(step.title)}</h3><p><strong>Do:</strong> ${escapeHtml(step.action)}</p><p><strong>Why:</strong> ${escapeHtml(step.why)}</p></div></article>`).join('');
  $('learning-sources').innerHTML = `Learn more: ${learning.sources.map((source) => `<a href="${escapeHtml(source.url)}" target="_blank" rel="noreferrer">${escapeHtml(source.label)}</a>`).join(' · ')}`;
}

fetch('/api/learning').then((response) => response.json()).then(renderLearning).catch((error) => { $('quality-vs-fair').textContent = error.message; });
