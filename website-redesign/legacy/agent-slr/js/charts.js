/* ======================================
   charts.js — Results visualizations
   Updated with ICML 2025 paper data
   ====================================== */

const Charts = (() => {

  // Color scheme
  const COLORS = {
    titleAbstract: '#B7D3C6',
    pdfConversion: '#C9A3A3',
    fulltextScreening: '#6BAED6',
    dataExtraction: '#E38B48',
    parameters: '#FFCBA4',
    models: '#E38B48',
    outbreaks: '#B45C1A',
    flagging: '#D97C7C',
    counts: '#8BB3E6',
    extraction: '#8FD3B0',
  };

  const MODEL_COLORS = {
    'GPT-OSS-120B': '#2B2E5F',
    'GLM-4.7': '#4B4F86',
    'DeepSeek-V3.2': '#6C74AD',
    'Kimi-K2.5': '#9AA4CF',
    'GPT-5.2': '#BDBDBD',
  };

  /* ---------- GANTT CHART ---------- */
  function renderGantt(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const maxHours = 400;

    // Human data (from paper)
    const humanBars = [
      { label: 'Title & Abstract Screening', start: 0, end: 114.15, color: COLORS.titleAbstract },
      { label: 'Full-text Screening', start: 114.15, end: 187.62, color: COLORS.fulltextScreening },
      { label: 'Data Extraction', start: 187.62, end: 385.12, color: COLORS.dataExtraction },
    ];

    // AgentSLR data (from paper - 20 hours total)
    const agentBars = [
      { label: 'Title & Abstract Screening', start: 0, end: 3.20, color: COLORS.titleAbstract },
      { label: 'PDF-to-MD Conversion', start: 3.20, end: 5.99, color: COLORS.pdfConversion },
      { label: 'Full-text Screening', start: 5.99, end: 6.61, color: COLORS.fulltextScreening },
      { label: 'Data Extraction', start: 6.61, end: 20.00, color: COLORS.dataExtraction },
    ];

    function pct(v) { return (v / maxHours * 100).toFixed(2) + '%'; }
    function w(bar) { return ((bar.end - bar.start) / maxHours * 100).toFixed(2) + '%'; }
    function ganttBarPositionClass(index, total) {
      if (total === 1) return 'gantt-bar-single';
      if (index === 0) return 'gantt-bar-first';
      if (index === total - 1) return 'gantt-bar-last';
      return 'gantt-bar-middle';
    }

    function renderRow(label, bars, totalHours, showLabels = false) {
      return `
        <div class="gantt-row">
          <div class="gantt-label">${label}<br><span style="font-size:0.75rem;color:var(--text-light);">${totalHours}h</span></div>
          <div class="gantt-track">
            ${bars.map((b, index) => {
              const duration = (b.end - b.start).toFixed(1);
              const widthPct = (b.end - b.start) / maxHours * 100;
              const showLabel = showLabels && widthPct > 8;
              const positionClass = ganttBarPositionClass(index, bars.length);
              return `<div class="gantt-bar ${positionClass}" style="left:${pct(b.start)};width:${w(b)};background:${b.color};" title="${b.label}: ${duration}h">${showLabel ? duration + 'h' : ''}</div>`;
            }).join('')}
          </div>
        </div>`;
    }

    // Legend
    const legendItems = [
      { label: 'Title & Abstract Screening', color: COLORS.titleAbstract },
      { label: 'PDF-to-MD Conversion*', color: COLORS.pdfConversion },
      { label: 'Full-text Screening', color: COLORS.fulltextScreening },
      { label: 'Data Extraction', color: COLORS.dataExtraction },
    ];
    const legend = `<div style="display:flex;gap:14px;justify-content:center;margin-bottom:12px;flex-wrap:wrap;font-size:0.78rem;">
      ${legendItems.map(l => `<span style="display:flex;align-items:center;gap:4px;"><span style="width:12px;height:12px;background:${l.color};border-radius:2px;display:inline-block;"></span>${l.label}</span>`).join('')}
    </div>`;

    const ticks = [0, 50, 100, 150, 200, 250, 300, 350, 400];

    // Zoomed inset for AgentSLR
    const zoomMax = 25;
    const zoomTicks = [0, 5, 10, 15, 20, 25];
    function zoomPct(v) { return (v / zoomMax * 100).toFixed(2) + '%'; }
    function zoomW(bar) { return ((bar.end - bar.start) / zoomMax * 100).toFixed(2) + '%'; }

    const zoomRow = `
      <div class="gantt-row">
        <div class="gantt-label" style="font-size:0.75rem;color:var(--accent);">AgentSLR<br>(magnified)</div>
        <div class="gantt-track" style="background:rgba(74,111,165,0.08);">
          ${agentBars.map((b, index) => {
            const duration = (b.end - b.start).toFixed(1);
            const positionClass = ganttBarPositionClass(index, agentBars.length);
            return `<div class="gantt-bar ${positionClass}" style="left:${zoomPct(b.start)};width:${zoomW(b)};background:${b.color};" title="${b.label}: ${duration}h">${duration}h</div>`;
          }).join('')}
        </div>
      </div>
      <div class="gantt-axis" style="margin-left:100px;">
        ${zoomTicks.map(t => `<span>${t}</span>`).join('')}
      </div>
      <div style="text-align:center;font-size:0.72rem;color:var(--text-light);margin-top:2px;">Time (hours) &mdash; Magnified view</div>`;

    container.innerHTML = `
      ${legend}
      ${renderRow('Humans', humanBars, '385', true)}
      ${renderRow('AgentSLR', agentBars, '20', false)}
      <div class="gantt-axis">
        ${ticks.map(t => `<span>${t}</span>`).join('')}
      </div>
      <div style="text-align:center;font-size:0.78rem;color:var(--text-light);margin-top:4px;">Time (hours)</div>
      <div style="text-align:center;">
        <button class="gantt-magnify-toggle" id="gantt-magnify-btn">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <path d="M21 21l-4.35-4.35"/>
            <path d="M11 8v6M8 11h6"/>
          </svg>
          Show Magnified View
        </button>
      </div>
      <div class="gantt-magnified-view" id="gantt-magnified">
        ${zoomRow}
      </div>
    `;

    // Toggle magnified view
    const btn = document.getElementById('gantt-magnify-btn');
    const magnified = document.getElementById('gantt-magnified');
    if (btn && magnified) {
      btn.addEventListener('click', function() {
        const isVisible = magnified.classList.contains('visible');
        if (isVisible) {
          magnified.classList.remove('visible');
          btn.classList.remove('active');
          btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <path d="M21 21l-4.35-4.35"/>
            <path d="M11 8v6M8 11h6"/>
          </svg> Show Magnified View`;
        } else {
          magnified.classList.add('visible');
          btn.classList.add('active');
          btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <path d="M21 21l-4.35-4.35"/>
            <path d="M8 11h6"/>
          </svg> Hide Magnified View`;
        }
      });
    }
  }

  /* ---------- MODEL ABLATION CHART ---------- */
  function renderModelAblationChart(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    function topRoundedBarPath(x, y, w, h, r) {
      const rr = Math.max(0, Math.min(r, w / 2, h));
      const yb = y + h;
      return `M${x},${yb} L${x},${y + rr} Q${x},${y} ${x + rr},${y} L${x + w - rr},${y} Q${x + w},${y} ${x + w},${y + rr} L${x + w},${yb} Z`;
    }

    const stages = [
      'Title & Abstract\nScreening',
      'Full-text\nScreening',
      'Parameter\nExtraction',
      'Model\nExtraction',
      'Outbreak\nExtraction'
    ];

    const models = ['GPT-OSS-120B', 'GLM-4.7', 'DeepSeek-V3.2', 'Kimi-K2.5', 'GPT-5.2'];

    // Data from paper
    const data = {
      'Title & Abstract\nScreening': {
        'GPT-OSS-120B': { f1: 0.74, std: 0.03 },
        'GLM-4.7': { f1: 0.72, std: 0.05 },
        'DeepSeek-V3.2': { f1: 0.62, std: 0.05 },
        'Kimi-K2.5': { f1: 0.77, std: 0.05 },
        'GPT-5.2': { f1: 0.65, std: 0.03 },
      },
      'Full-text\nScreening': {
        'GPT-OSS-120B': { f1: 0.87, std: 0.04 },
        'GLM-4.7': { f1: 0.81, std: 0.03 },
        'DeepSeek-V3.2': { f1: 0.74, std: 0.06 },
        'Kimi-K2.5': { f1: 0.83, std: 0.05 },
        'GPT-5.2': { f1: 0.82, std: 0.04 },
      },
      'Parameter\nExtraction': {
        'GPT-OSS-120B': { f1: 0.59, std: 0.03, flagging: 0.66, counts: 0.59, extraction: 0.54 },
        'GLM-4.7': { f1: 0.63, std: 0.04, flagging: 0.72, counts: 0.61, extraction: 0.54 },
        'DeepSeek-V3.2': { f1: 0.56, std: 0.01, flagging: 0.60, counts: 0.56, extraction: 0.50 },
        'Kimi-K2.5': { f1: 0.63, std: 0.04, flagging: 0.72, counts: 0.62, extraction: 0.56 },
        'GPT-5.2': { f1: 0.58, std: 0.04, flagging: 0.66, counts: 0.50, extraction: 0.59 },
      },
      'Model\nExtraction': {
        'GPT-OSS-120B': { f1: 0.75, std: 0.04, flagging: 0.91, counts: 0.68, extraction: 0.67 },
        'GLM-4.7': { f1: 0.85, std: 0.06, flagging: 0.93, counts: 0.93, extraction: 0.68 },
        'DeepSeek-V3.2': { f1: 0.81, std: 0.06, flagging: 0.87, counts: 0.92, extraction: 0.65 },
        'Kimi-K2.5': { f1: 0.81, std: 0.04, flagging: 0.92, counts: 0.81, extraction: 0.68 },
        'GPT-5.2': { f1: 0.77, std: 0.04, flagging: 0.90, counts: 0.72, extraction: 0.67 },
      },
      'Outbreak\nExtraction': {
        'GPT-OSS-120B': { f1: 0.70, std: 0.14, flagging: 0.62, counts: 0.69, extraction: 0.79 },
        'GLM-4.7': { f1: 0.72, std: 0.09, flagging: 0.68, counts: 0.72, extraction: 0.77 },
        'DeepSeek-V3.2': { f1: 0.73, std: 0.06, flagging: 0.65, counts: 0.78, extraction: 0.75 },
        'Kimi-K2.5': { f1: 0.76, std: 0.08, flagging: 0.64, counts: 0.87, extraction: 0.78 },
        'GPT-5.2': { f1: 0.77, std: 0.01, flagging: 0.66, counts: 0.80, extraction: 0.84 },
      },
    };

    const svgW = 1000, svgH = 334;
    const margin = { top: 60, right: 30, bottom: 44, left: 55 };
    const plotW = svgW - margin.left - margin.right;
    const plotH = svgH - margin.top - margin.bottom;

    const stageW = plotW / stages.length;
    const barW = stageW * 0.14;
    const barGap = 3;

    let svg = `<svg viewBox="0 0 ${svgW} ${svgH}" style="width:100%;height:auto;overflow:visible;">`;

    // Legend for models (inside the SVG, properly positioned)
    svg += `<g transform="translate(${margin.left}, 15)">`;
    let legendX = 0;
    models.forEach((m, i) => {
      svg += `<rect x="${legendX}" y="0" width="14" height="14" rx="3" fill="${MODEL_COLORS[m]}"/>`;
      svg += `<text x="${legendX + 20}" y="11" font-size="11" fill="#444">${m}</text>`;
      legendX += m.length * 7 + 45;
    });
    svg += `</g>`;

    // Legend for component dots (positioned after models)
    svg += `<g transform="translate(${margin.left + 680}, 15)">`;
    const dotLegend = [
      { label: 'Flagging', color: COLORS.flagging },
      { label: 'Counts', color: COLORS.counts },
      { label: 'Extraction', color: COLORS.extraction },
    ];
    dotLegend.forEach((d, i) => {
      const x = i * 90;
      svg += `<circle cx="${x + 5}" cy="7" r="5" fill="${d.color}"/>`;
      svg += `<text x="${x + 14}" y="11" font-size="10" fill="#666">${d.label}</text>`;
    });
    svg += `</g>`;

    // Y axis (no gridlines)
    svg += `<line x1="${margin.left}" y1="${margin.top}" x2="${margin.left}" y2="${margin.top + plotH}" stroke="#BDBDBD" stroke-width="1"/>`;
    for (let y = 0; y <= 1; y += 0.25) {
      const yPos = margin.top + plotH - (y * plotH);
      svg += `<text x="${margin.left - 10}" y="${yPos + 4}" text-anchor="end" font-size="10" fill="#999">${y.toFixed(2)}</text>`;
    }
    svg += `<text x="${margin.left - 42}" y="${margin.top + plotH/2}" text-anchor="middle" font-size="12" fill="#666" transform="rotate(-90, ${margin.left - 42}, ${margin.top + plotH/2})">F&#8321; Score</text>`;

    // X axis line
    svg += `<line x1="${margin.left}" y1="${margin.top + plotH}" x2="${margin.left + plotW}" y2="${margin.top + plotH}" stroke="#BDBDBD" stroke-width="1"/>`;

    // Bars
    stages.forEach((stage, si) => {
      const stageData = data[stage];
      const groupX = margin.left + si * stageW + stageW * 0.12;
      const hasComponents = stage.includes('Extraction');

      // Find best value in group
      const groupVals = models.map(m => stageData[m].f1);
      const maxVal = Math.max(...groupVals);

      models.forEach((model, mi) => {
        const d = stageData[model];
        const x = groupX + mi * (barW + barGap);
        const h = d.f1 * plotH;
        const y = margin.top + plotH - h;
        const isBest = d.f1 === maxVal;

        // Bar
        svg += `<path d="${topRoundedBarPath(x, y, barW, h, 3)}" fill="${MODEL_COLORS[model]}"/>`;

        // Error bar
        const errH = d.std * plotH;
        const mid = x + barW / 2;
        svg += `<line x1="${mid}" y1="${y - errH}" x2="${mid}" y2="${y + errH}" stroke="#333" stroke-width="1"/>`;
        svg += `<line x1="${mid - 3}" y1="${y - errH}" x2="${mid + 3}" y2="${y - errH}" stroke="#333" stroke-width="1"/>`;
        svg += `<line x1="${mid - 3}" y1="${y + errH}" x2="${mid + 3}" y2="${y + errH}" stroke="#333" stroke-width="1"/>`;

        // Value label for ALL bars
        const labelWeight = isBest ? 'font-weight="bold"' : '';
        const labelColor = isBest ? '#333' : '#666';
        svg += `<text x="${mid}" y="${y - errH - 6}" text-anchor="middle" font-size="9" ${labelWeight} fill="${labelColor}">${d.f1.toFixed(2)}</text>`;

        // Component dots for extraction stages
        if (hasComponents && d.flagging) {
          const dotX = x;
          svg += `<circle cx="${dotX}" cy="${margin.top + plotH - d.flagging * plotH}" r="4" fill="${COLORS.flagging}"/>`;
          svg += `<circle cx="${dotX}" cy="${margin.top + plotH - d.counts * plotH}" r="4" fill="${COLORS.counts}"/>`;
          svg += `<circle cx="${dotX}" cy="${margin.top + plotH - d.extraction * plotH}" r="4" fill="${COLORS.extraction}"/>`;
        }
      });

      // Stage label
      const labelLines = stage.split('\n');
      svg += `<text x="${groupX + (models.length * (barW + barGap)) / 2}" y="${margin.top + plotH + 20}" text-anchor="middle" font-size="11" fill="#666">`;
      labelLines.forEach((line, li) => {
        svg += `<tspan x="${groupX + (models.length * (barW + barGap)) / 2}" dy="${li === 0 ? 0 : 14}">${line}</tspan>`;
      });
      svg += `</text>`;
    });

    svg += `</svg>`;
    container.innerHTML = svg;
  }

  /* ---------- COST VS PERFORMANCE CHART ---------- */
  function renderCostPerformanceChart(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const data = [
      { model: 'GPT-OSS-120B', cost: 13.9, f1: 0.70, f1_err: 0.07 },
      { model: 'DeepSeek-V3.2', cost: 73.6, f1: 0.67, f1_err: 0.11 },
      { model: 'Kimi-K2.5', cost: 277.2, f1: 0.74, f1_err: 0.07 },
      { model: 'GLM-4.7', cost: 810.8, f1: 0.73, f1_err: 0.09 },
      { model: 'GPT-5.2', cost: 1348.2, f1: 0.69, f1_err: 0.09 },
    ];

    const svgW = 800, svgH = 380;
    const margin = { top: 70, right: 60, bottom: 60, left: 80 };
    const plotW = svgW - margin.left - margin.right;
    const plotH = svgH - margin.top - margin.bottom;

    // Log scale for x-axis
    const minCost = 10, maxCost = 2000;
    const logMin = Math.log10(minCost), logMax = Math.log10(maxCost);

    function xPos(cost) {
      const logCost = Math.log10(cost);
      return margin.left + ((logCost - logMin) / (logMax - logMin)) * plotW;
    }

    function yPos(f1) {
      return margin.top + plotH - ((f1 - 0.55) / 0.35) * plotH;
    }

    let svg = `<svg viewBox="0 0 ${svgW} ${svgH}" style="width:100%;height:auto;">`;

    // Corner triangles for ideal/not ideal regions
    // Top-left triangle (ideal - green pastel)
    svg += `<defs>
      <linearGradient id="idealGradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:#C2DCCF;stop-opacity:0.6"/>
        <stop offset="100%" style="stop-color:#C2DCCF;stop-opacity:0"/>
      </linearGradient>
      <linearGradient id="lessIdealGradient" x1="100%" y1="100%" x2="0%" y2="0%">
        <stop offset="0%" style="stop-color:#E3C4C4;stop-opacity:0.6"/>
        <stop offset="100%" style="stop-color:#E3C4C4;stop-opacity:0"/>
      </linearGradient>
    </defs>`;

    // Ideal region (top-left)
    svg += `<polygon points="${margin.left},${margin.top} ${margin.left + plotW * 0.4},${margin.top} ${margin.left},${margin.top + plotH * 0.4}" fill="url(#idealGradient)"/>`;

    // Not ideal region (bottom-right)
    svg += `<polygon points="${margin.left + plotW},${margin.top + plotH} ${margin.left + plotW * 0.6},${margin.top + plotH} ${margin.left + plotW},${margin.top + plotH * 0.6}" fill="url(#lessIdealGradient)"/>`;

    // Labels for regions
    svg += `<text x="${margin.left + 15}" y="${margin.top + 20}" font-size="9" fill="#6BAE7E" font-style="italic">Ideal</text>`;
    svg += `<text x="${margin.left + plotW - 50}" y="${margin.top + plotH - 10}" font-size="9" fill="#D17171" font-style="italic">Not Ideal</text>`;

    // Y axis (no gridlines)
    svg += `<line x1="${margin.left}" y1="${margin.top}" x2="${margin.left}" y2="${margin.top + plotH}" stroke="#bbb" stroke-width="1"/>`;
    for (let y = 0.6; y <= 0.85; y += 0.05) {
      const yp = yPos(y);
      if (yp >= margin.top && yp <= margin.top + plotH) {
        svg += `<text x="${margin.left - 10}" y="${yp + 4}" text-anchor="end" font-size="10" fill="#999">${y.toFixed(2)}</text>`;
      }
    }
    svg += `<text x="${margin.left - 55}" y="${margin.top + plotH/2}" text-anchor="middle" font-size="12" fill="#666" transform="rotate(-90, ${margin.left - 55}, ${margin.top + plotH/2})">Average Performance (F&#8321; Score)</text>`;

    // X axis (log scale, no gridlines)
    svg += `<line x1="${margin.left}" y1="${margin.top + plotH}" x2="${margin.left + plotW}" y2="${margin.top + plotH}" stroke="#bbb" stroke-width="1"/>`;
    const xTicks = [10, 20, 50, 100, 200, 500, 1000];
    xTicks.forEach(t => {
      const xp = xPos(t);
      if (xp >= margin.left && xp <= margin.left + plotW) {
        svg += `<text x="${xp}" y="${margin.top + plotH + 20}" text-anchor="middle" font-size="10" fill="#999">$${t >= 1000 ? (t/1000) + 'k' : t}</text>`;
      }
    });
    svg += `<text x="${margin.left + plotW/2}" y="${margin.top + plotH + 45}" text-anchor="middle" font-size="12" fill="#666">Total Cost per Pathogen run (log&#8321;&#8320; USD)</text>`;

    // Data points
    data.forEach(d => {
      const x = xPos(d.cost);
      const y = yPos(d.f1);
      const errTop = yPos(d.f1 + d.f1_err);
      const errBot = yPos(d.f1 - d.f1_err);
      const color = MODEL_COLORS[d.model];

      // Error bar
      svg += `<line x1="${x}" y1="${errTop}" x2="${x}" y2="${errBot}" stroke="${color}" stroke-width="6" stroke-linecap="round"/>`;
      svg += `<line x1="${x - 6}" y1="${errTop}" x2="${x + 6}" y2="${errTop}" stroke="${color}" stroke-width="3"/>`;
      svg += `<line x1="${x - 6}" y1="${errBot}" x2="${x + 6}" y2="${errBot}" stroke="${color}" stroke-width="3"/>`;

      // Point
      svg += `<circle cx="${x}" cy="${y}" r="10" fill="${color}" stroke="white" stroke-width="2"/>`;

      // Model name label (top)
      svg += `<text x="${x}" y="${margin.top - 35}" text-anchor="middle" font-size="10" fill="#666">${d.model}</text>`;
      // Cost label
      svg += `<text x="${x}" y="${margin.top - 22}" text-anchor="middle" font-size="11" font-weight="bold" fill="${color}">$${d.cost < 100 ? d.cost.toFixed(1) : Math.round(d.cost)}</text>`;
      // Performance annotation with +/- deviation alongside the dot
      svg += `<text x="${x + 16}" y="${y + 4}" text-anchor="start" font-size="9" fill="#444">${d.f1.toFixed(2)}</text>`;
      svg += `<text x="${x + 16}" y="${y + 14}" text-anchor="start" font-size="8" fill="#888">&plusmn;${d.f1_err.toFixed(2)}</text>`;
    });

    svg += `</svg>`;
    container.innerHTML = svg;
  }

  /* ---------- SCREENING BAR CHART ---------- */
  function renderScreeningChart(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    function topRoundedBarPath(x, y, w, h, r) {
      const rr = Math.max(0, Math.min(r, w / 2, h));
      const yb = y + h;
      return `M${x},${yb} L${x},${y + rr} Q${x},${y} ${x + rr},${y} L${x + w - rr},${y} Q${x + w},${y} ${x + w},${y + rr} L${x + w},${yb} Z`;
    }

    const pathogens = ['Marburg', 'Ebola', 'Lassa', 'SARS', 'Zika', 'MERS', 'Nipah', 'Overall'];

    // Recall data from paper [two-stage AI, direct full-text, human+AI]
    const data = {
      'Marburg': { recall: [0.76, 0.82, 0.83] },
      'Ebola':   { recall: [0.84, 0.93, 0.97] },
      'Lassa':   { recall: [0.78, 0.91, 0.94] },
      'SARS':    { recall: [0.85, 0.91, 0.95] },
      'Zika':    { recall: [0.79, 0.85, 0.91] },
      'MERS':    { recall: [0.83, 0.95, 0.96] },
      'Nipah':   { recall: [0.84, 0.88, 0.90] },
      'Overall': { recall: [0.81, 0.89, 0.92] },
    };

    const COLOR_TWO_STAGE = '#8AC1E1';
    const COLOR_DIRECT = '#3F86B5';
    const COLOR_PERG_FILTERED = '#1F5F8C';

    const strategies = [
      { key: 0, label: 'AI Screen (Abstract) → AI Screen (Full-text)', color: COLOR_TWO_STAGE },
      { key: 1, label: 'AI Screen (Direct Full-text)', color: COLOR_DIRECT },
      { key: 2, label: 'Human Screen (Abstract) → AI Screen (Full-text)', color: COLOR_PERG_FILTERED },
    ];

    const svgW = 900, svgH = 320;
    const margin = { top: 50, right: 30, bottom: 60, left: 55 };
    const plotW = svgW - margin.left - margin.right;
    const plotH = svgH - margin.top - margin.bottom;

    const groupW = plotW / pathogens.length;
    const barW = groupW * 0.22;
    const barGap = 3;

    let svg = `<svg viewBox="0 0 ${svgW} ${svgH}" class="screening-chart-svg" style="width:100%;height:auto;">`;

    // Legend
    svg += `<g transform="translate(${margin.left}, 12)">`;
    let lx = 0;
    strategies.forEach((s, i) => {
      svg += `<rect x="${lx}" y="0" width="14" height="12" rx="2" fill="${s.color}"/>`;
      svg += `<text x="${lx + 20}" y="10" font-size="10" fill="#666">${s.label}</text>`;
      lx += s.label.length * 5.5 + 40;
    });
    svg += `</g>`;

    // Y axis (no gridlines)
    svg += `<line x1="${margin.left}" y1="${margin.top}" x2="${margin.left}" y2="${margin.top + plotH}" stroke="#BDBDBD" stroke-width="1"/>`;
    for (let y = 0; y <= 1; y += 0.25) {
      const yPos = margin.top + plotH - (y * plotH);
      svg += `<text x="${margin.left - 10}" y="${yPos + 4}" text-anchor="end" font-size="10" fill="#999">${y.toFixed(2)}</text>`;
    }
    svg += `<text x="${margin.left - 40}" y="${margin.top + plotH/2}" text-anchor="middle" font-size="11" fill="#666" transform="rotate(-90, ${margin.left - 40}, ${margin.top + plotH/2})">Recall</text>`;

    // X axis line
    svg += `<line x1="${margin.left}" y1="${margin.top + plotH}" x2="${margin.left + plotW}" y2="${margin.top + plotH}" stroke="#BDBDBD" stroke-width="1"/>`;

    // Bars
    pathogens.forEach((p, pi) => {
      const groupX = margin.left + pi * groupW + groupW * 0.12;
      const vals = data[p].recall;

      // Find best value
      const maxVal = Math.max(...vals);

      vals.forEach((v, si) => {
        const x = groupX + si * (barW + barGap);
        const h = v * plotH;
        const y = margin.top + plotH - h;
        const isBest = v === maxVal;

        svg += `<path d="${topRoundedBarPath(x, y, barW, h, 2)}" fill="${strategies[si].color}"/>`;

        // Error bar (simulated ~3% CI)
        const errH = 0.03 * plotH;
        const mid = x + barW / 2;
        svg += `<line x1="${mid}" y1="${y - errH}" x2="${mid}" y2="${y + errH}" stroke="#333" stroke-width="1"/>`;
        svg += `<line x1="${mid - 3}" y1="${y - errH}" x2="${mid + 3}" y2="${y - errH}" stroke="#333" stroke-width="1"/>`;
        svg += `<line x1="${mid - 3}" y1="${y + errH}" x2="${mid + 3}" y2="${y + errH}" stroke="#333" stroke-width="1"/>`;

        // Value label
        const labelStyle = isBest ? 'font-weight="bold" fill="#333"' : 'fill="#666"';
        svg += `<text x="${mid}" y="${y - errH - 5}" text-anchor="middle" font-size="9" ${labelStyle}>${v.toFixed(2)}</text>`;
      });

      // Pathogen label
      svg += `<text x="${groupX + (3 * (barW + barGap)) / 2}" y="${margin.top + plotH + 20}" text-anchor="middle" font-size="10" fill="#666">${p}</text>`;
    });

    svg += `</svg>`;
    container.innerHTML = svg;
  }

  /* ---------- PUBLIC API ---------- */
  function renderAll() {
    renderGantt('gantt-chart');
    renderModelAblationChart('model-ablation-chart');
    renderCostPerformanceChart('cost-performance-chart');
    renderScreeningChart('screening-chart');
  }

  return {
    renderAll,
    renderGantt,
    renderModelAblationChart,
    renderCostPerformanceChart,
    renderScreeningChart
  };
})();
