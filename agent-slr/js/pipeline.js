/* ======================================
   pipeline.js — Pipeline animation engine
   ====================================== */

const Pipeline = (() => {
  let running = false;
  let aborted = false;
  let hasStarted = false;
  let data = null;

  const STAGES = 6;
  const STAGE_SETTINGS = {
    // durationMs controls approximate stage runtime.
    // displayLimit controls how many entries are shown in that card log (null = all).
    1: { durationMs: 5500, displayLimit: 60 },
    2: { durationMs: 6000, displayLimit: 60 },
    3: { durationMs: 5500, displayLimit: 60 },
    4: { durationMs: 6000, displayLimit: 60 },
    5: { durationMs: 4000, displayLimit: { params: 8, models: 5, outbreaks: 5 } },
    6: { durationMs: 5500 },
  };

  /* ---------- HELPERS ---------- */
  function sleep(ms) {
    return new Promise(r => {
      const id = setTimeout(r, ms);
      // store so we can abort
      if (aborted) { clearTimeout(id); r(); }
    });
  }

  function getDisplayCount(stage, total, kind = null) {
    const stageCfg = STAGE_SETTINGS[stage] || {};
    let limit = stageCfg.displayLimit;
    if (limit && typeof limit === 'object') limit = limit[kind];
    if (limit === null || limit === undefined || Number(limit) <= 0) return total;
    return Math.min(total, Number(limit));
  }

  function getPerItemDelayRange(stage, items, fixedMs = 0, minMs = 10, maxMs = 140) {
    const target = (STAGE_SETTINGS[stage] || {}).durationMs;
    if (!target || items <= 0) return { min: minMs, max: maxMs };
    const budget = Math.max(0, target - fixedMs);
    const center = Math.max(minMs, Math.floor(budget / items));
    const jitter = Math.max(0, Math.floor(center * 0.3));
    return {
      min: Math.max(minMs, center - jitter),
      max: Math.min(maxMs, center + jitter),
    };
  }

  function getCard(stage) { return document.querySelector(`.pipeline-card[data-stage="${stage}"]`); }
  function getLog(stage) { return document.getElementById(`log-${stage}`); }
  function getProgress(stage) { return document.getElementById(`progress-${stage}`); }
  function getStatus(stage) { return document.getElementById(`status-${stage}`); }

  function setProgress(stage, pct) {
    const el = getProgress(stage);
    if (!el) return;
    el.style.display = 'block';
    el.querySelector('.progress-fill').style.width = pct + '%';
    el.querySelector('.progress-text').textContent = Math.round(pct) + '%';
  }

  function addLog(stage, text, cls = 'log-info') {
    const log = getLog(stage);
    if (!log) return;
    const shouldFollow = stage <= 4;
    const entry = document.createElement('div');
    entry.className = `log-entry ${cls}`;
    entry.textContent = text;
    log.appendChild(entry);
    if (shouldFollow) {
      requestAnimationFrame(() => {
        log.scrollTo({ top: log.scrollHeight, behavior: 'smooth' });
      });
    }
  }

  function setStatus(stage, text) {
    const el = getStatus(stage);
    if (el) el.textContent = text;
  }

  function activateStage(stage) {
    for (let i = 1; i <= STAGES; i++) {
      const card = getCard(i);
      if (!card) continue;
      card.classList.remove('active', 'dimmed');
      if (i === stage) card.classList.add('active');
      else if (i > stage) card.classList.add('dimmed');
    }
  }

  function completeStage(stage) {
    const card = getCard(stage);
    if (card) {
      card.classList.remove('active');
      card.classList.add('completed');
    }
  }

  function truncate(str, len = 50) {
    if (!str) return '(untitled)';
    return str.length > len ? str.substring(0, len) + '...' : str;
  }

  /* ---------- ANIMATION STAGES ---------- */

  async function runStage1(d) {
    activateStage(1);
    setStatus(1, 'Fetching articles from OpenAlex, PubMed, Europe PMC...');
    setProgress(1, 0);

    // Use abstract file rows as the fetched set for stage 1 stats/display.
    const articles = d.abstractScreen || [];
    const total = getDisplayCount(1, articles.length);
    const itemDelay = getPerItemDelayRange(1, total, 600 + 400 + 400, 10, 80);
    addLog(1, `Sending Boolean search queries...`, 'log-info');
    await sleep(600);
    addLog(1, `Sources: OpenAlex (30 req/s), PubMed, Europe PMC (20 req/s)`, 'log-info');
    await sleep(400);

    for (let i = 0; i < total; i++) {
      if (aborted) return;
      const a = articles[i];
      const title = truncate(a.title || a.article_id, 45);
      addLog(1, `Fetched: ${title} (${a.year || '?'})`, 'log-info');
      setProgress(1, ((i + 1) / total) * 100);
      await sleep(itemDelay.min + Math.random() * (itemDelay.max - itemDelay.min));
    }

    addLog(1, `Total: ${articles.length} articles retrieved`, 'log-info');
    addLog(1, `Deduplication by DOI/PMID/PMCID complete`, 'log-info');
    setProgress(1, 100);
    setStatus(1, `${articles.length} articles fetched`);
    completeStage(1);
    await sleep(400);
  }

  async function runStage2(d) {
    activateStage(2);
    setStatus(2, 'Screening titles and abstracts...');
    setProgress(2, 0);

    const articles = d.abstractScreen || [];
    const total = getDisplayCount(2, articles.length);
    const itemDelay = getPerItemDelayRange(2, total, 500 + 400, 10, 90);

    addLog(2, `Applying inclusion/exclusion criteria...`, 'log-info');
    await sleep(500);

    let included = 0, excluded = 0;
    for (let i = 0; i < total; i++) {
      if (aborted) return;
      const a = articles[i];
      const title = truncate(a.title || a.article_id, 40);
      const decision = (a.ai4epi_abstract_decision || '').toUpperCase();
      if (decision.includes('INCLUDE')) {
        addLog(2, `\u2713 Included: ${title}`, 'log-include');
        included++;
      } else {
        addLog(2, `\u2717 Excluded: ${title}`, 'log-exclude');
        excluded++;
      }
      setProgress(2, ((i + 1) / total) * 100);
      await sleep(itemDelay.min + Math.random() * (itemDelay.max - itemDelay.min));
    }

    // Count totals from full data
    const totalInc = articles.filter(a => (a.ai4epi_abstract_decision || '').toUpperCase().includes('INCLUDE')).length;
    const totalExc = articles.length - totalInc;

    setProgress(2, 100);
    addLog(2, `Total: ${totalInc} included, ${totalExc} excluded`, 'log-info');
    setStatus(2, `${totalInc} included / ${totalExc} excluded`);
    completeStage(2);
    await sleep(400);
  }

  async function runStage3(d) {
    activateStage(3);
    setStatus(3, 'Converting PDFs to Markdown via OCR...');
    setProgress(3, 0);
    const stageStart = Date.now();

    // Use included articles for conversion count
    const included = (d.abstractScreen || []).filter(a =>
      (a.ai4epi_abstract_decision || '').toUpperCase().includes('INCLUDE')
    );
    const total = getDisplayCount(3, included.length);
    const itemDelay = getPerItemDelayRange(3, total, 500 + 400, 10, 90);

    addLog(3, `Mistral OCR 3 initialized`, 'log-info');
    addLog(3, `Rendering PDFs page-by-page...`, 'log-info');
    await sleep(500);

    for (let i = 0; i < total; i++) {
      if (aborted) return;
      const title = truncate(included[i].title || included[i].article_id, 38);
      const pages = 5 + Math.floor(Math.random() * 15);
      addLog(3, `OCR: ${title} (${pages} pages)`, 'log-info');
      setProgress(3, ((i + 1) / total) * 100);
      await sleep(itemDelay.min + Math.random() * (itemDelay.max - itemDelay.min));
    }

    addLog(3, `LaTeX equations preserved, HTML tables maintained`, 'log-info');
    setProgress(3, 100);
    const elapsedSec = ((Date.now() - stageStart) / 1000).toFixed(1);
    setStatus(3, `${included.length} documents converted in ${elapsedSec}s`);
    completeStage(3);
    await sleep(400);
  }

  async function runStage4(d) {
    activateStage(4);
    setStatus(4, 'Full-text screening in progress...');
    setProgress(4, 0);

    const abstractIncluded = (d.abstractScreen || []).filter(a =>
      (a.ai4epi_abstract_decision || '').toUpperCase().includes('INCLUDE')
    );
    const fulltextById = new Map((d.fulltextScreen || []).map(a => [a.article_id, a]));
    // Only evaluate items included at abstract stage; missing full-text decisions are treated as excluded.
    const articles = abstractIncluded.map(a => fulltextById.get(a.article_id) || {
      title: a.title,
      article_id: a.article_id,
      ai4epi_fulltext_decision: 'EXCLUDE',
    });
    const total = getDisplayCount(4, articles.length);
    const itemDelay = getPerItemDelayRange(4, total, 400 + 400, 10, 100);

    addLog(4, `Evaluating full-text against inclusion criteria...`, 'log-info');
    await sleep(400);

    let included = 0, excluded = 0;
    for (let i = 0; i < total; i++) {
      if (aborted) return;
      const a = articles[i];
      const title = truncate(a.title || a.article_id, 38);
      const decision = (a.ai4epi_fulltext_decision || '').toUpperCase();
      if (decision.includes('INCLUDE')) {
        addLog(4, `\u2713 Selected: ${title} \u2014 inclusion criteria met`, 'log-include');
        included++;
      } else {
        addLog(4, `\u2717 AgentSLR rejected: ${title}`, 'log-exclude');
        excluded++;
      }
      setProgress(4, ((i + 1) / total) * 100);
      await sleep(itemDelay.min + Math.random() * (itemDelay.max - itemDelay.min));
    }

    const totalInc = articles.filter(a => (a.ai4epi_fulltext_decision || '').toUpperCase().includes('INCLUDE')).length;
    const totalExc = articles.length - totalInc;

    setProgress(4, 100);
    addLog(4, `Total: ${totalInc} included, ${totalExc} excluded`, 'log-info');
    setStatus(4, `${totalInc} included / ${totalExc} excluded`);
    completeStage(4);
    await sleep(400);
  }

  async function runStage5(d) {
    activateStage(5);
    setStatus(5, 'Extracting parameters, models, outbreaks...');
    setProgress(5, 0);

    const params = d.parameters || [];
    const models = d.models || [];
    const outbreaks = d.outbreaks || [];

    addLog(5, `Extracting from ${new Set([...params, ...models, ...outbreaks].map(x => x.article_id)).size} articles...`, 'log-info');
    await sleep(400);

    // Show parameters
    const paramSample = params.slice(0, getDisplayCount(5, params.length, 'params'));
    const modelSample = models.slice(0, getDisplayCount(5, models.length, 'models'));
    const outSample = outbreaks.slice(0, getDisplayCount(5, outbreaks.length, 'outbreaks'));
    const totalStageItems = paramSample.length + modelSample.length + outSample.length;
    const itemDelay = getPerItemDelayRange(5, totalStageItems, 400 + 400, 20, 140);
    for (let i = 0; i < paramSample.length; i++) {
      if (aborted) return;
      const p = paramSample[i];
      const cls = p.parameter_class || 'parameter';
      const val = p.value ? `: ${p.value} ${p.unit || ''}` : '';
      addLog(5, `[Param] ${cls}${val} (${p.article_id})`, 'log-info');
      setProgress(5, (i / Math.max(totalStageItems, 1)) * 100);
      await sleep(itemDelay.min + Math.random() * (itemDelay.max - itemDelay.min));
    }

    // Show models
    for (let i = 0; i < modelSample.length; i++) {
      if (aborted) return;
      const m = modelSample[i];
      addLog(5, `[Model] ${m.model_type || 'Unknown'} \u2014 ${m.compartmental_type || ''} (${m.article_id})`, 'log-info');
      setProgress(5, ((paramSample.length + i) / Math.max(totalStageItems, 1)) * 100);
      await sleep(itemDelay.min + Math.random() * (itemDelay.max - itemDelay.min));
    }

    // Show outbreaks
    for (let i = 0; i < outSample.length; i++) {
      if (aborted) return;
      const o = outSample[i];
      const loc = o.outbreak_country || 'Unknown';
      const year = o.outbreak_start_year || '?';
      addLog(5, `[Outbreak] ${loc}, ${year} \u2014 ${o.cases_confirmed || '?'} confirmed cases (${o.article_id})`, 'log-info');
      setProgress(5, ((paramSample.length + modelSample.length + i) / Math.max(totalStageItems, 1)) * 100);
      await sleep(itemDelay.min + Math.random() * (itemDelay.max - itemDelay.min));
    }

    setProgress(5, 100);
    addLog(5, `Extracted: ${params.length} parameters, ${models.length} models, ${outbreaks.length} outbreaks`, 'log-info');
    setStatus(5, `${params.length} params / ${models.length} models / ${outbreaks.length} outbreaks`);
    completeStage(5);
    await sleep(400);
  }

  async function runStage6(d) {
    activateStage(6);
    setStatus(6, 'Generating reports...');
    setProgress(6, 0);
    const stageTarget = (STAGE_SETTINGS[6] || {}).durationMs;
    const stageBase = 600 + 500 + 700 + (5 * (400 + 350)) + 300;
    const stageScale = stageTarget ? stageTarget / stageBase : 1;
    const sleep6 = (ms) => sleep(Math.max(5, Math.round(ms * stageScale)));

    addLog(6, `Computing descriptive statistics...`, 'log-info');
    await sleep6(600);
    setProgress(6, 10);

    addLog(6, `Building evidence tables...`, 'log-info');
    await sleep6(500);
    setProgress(6, 20);

    addLog(6, `Passing to LLM for narrative synthesis...`, 'log-info');
    await sleep6(700);
    setProgress(6, 35);

    // Self-refinement loop
    for (let k = 1; k <= 5; k++) {
      if (aborted) return;
      addLog(6, `Self-refinement iteration ${k}/5: critiquing...`, 'log-info');
      await sleep6(400);
      addLog(6, `Iteration ${k}/5: revising across 8 dimensions...`, 'log-info');
      await sleep6(350);
      setProgress(6, 35 + (k / 5) * 55);
    }

    addLog(6, `Verification of claims complete`, 'log-info');
    setProgress(6, 95);
    await sleep6(300);

    // Show report snippets
    if (d.modelsReport) {
      const snippet = d.modelsReport.substring(0, 80).replace(/\n/g, ' ');
      addLog(6, `Models report: "${snippet}..."`, 'log-info');
    }
    if (d.outbreaksReport) {
      const snippet = d.outbreaksReport.substring(0, 80).replace(/\n/g, ' ');
      addLog(6, `Outbreaks report: "${snippet}..."`, 'log-info');
    }

    setProgress(6, 100);
    setStatus(6, 'Reports generated');
    completeStage(6);

    // Enable report actions
    ['view-models-md', 'view-outbreaks-md'].forEach(id => {
      const btn = document.getElementById(id);
      if (btn) btn.style.display = 'inline-block';
    });
  }

  /* ---------- MAIN RUN ---------- */
  async function run(pathogenData) {
    if (running) return;
    running = true;
    aborted = false;
    hasStarted = true;
    data = pathogenData;

    // Reset all cards
    for (let i = 1; i <= STAGES; i++) {
      const card = getCard(i);
      if (card) {
        card.classList.remove('completed', 'active', 'flipped', 'dimmed');
        card.dataset.pinned = 'false';
        card.classList.add('dimmed');
      }
      const log = getLog(i);
      if (log) log.innerHTML = '';
      const prog = getProgress(i);
      if (prog) {
        prog.style.display = 'none';
        prog.querySelector('.progress-fill').style.width = '0%';
      }
      setStatus(i, '');
    }
    ['view-models-md', 'view-outbreaks-md'].forEach(id => {
      const btn = document.getElementById(id);
      if (btn) btn.style.display = 'none';
    });

    await runStage1(data);
    if (aborted) return finish();
    await runStage2(data);
    if (aborted) return finish();
    await runStage3(data);
    if (aborted) return finish();
    await runStage4(data);
    if (aborted) return finish();
    await runStage5(data);
    if (aborted) return finish();
    await runStage6(data);

    finish();
  }

  function finish() {
    running = false;
    // Remove dimmed from all
    for (let i = 1; i <= STAGES; i++) {
      const card = getCard(i);
      if (card) card.classList.remove('dimmed', 'active');
    }
  }

  function reset() {
    aborted = true;
    running = false;
    hasStarted = false;
    data = null;
    for (let i = 1; i <= STAGES; i++) {
      const card = getCard(i);
      if (card) {
        card.classList.remove('completed', 'active', 'flipped', 'dimmed');
        card.dataset.pinned = 'false';
      }
      const log = getLog(i);
      if (log) log.innerHTML = '';
      const prog = getProgress(i);
      if (prog) {
        prog.style.display = 'none';
        prog.querySelector('.progress-fill').style.width = '0%';
      }
      setStatus(i, '');
    }
    ['view-models-md', 'view-outbreaks-md'].forEach(id => {
      const btn = document.getElementById(id);
      if (btn) btn.style.display = 'none';
    });
  }

  function isRunning() { return running; }
  function hasRunStarted() { return hasStarted; }
  function getData() { return data; }

  return { run, reset, isRunning, hasRunStarted, getData };
})();
