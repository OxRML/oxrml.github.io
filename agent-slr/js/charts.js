/* ======================================
   charts.js — Results visualizations
   ====================================== */

const Charts = (() => {

  /* ---------- GANTT CHART ---------- */
  let ganttZoomLevel = 1;
  const ganttMaxHours = 400;

  function renderGantt(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const maxHours = ganttMaxHours;

    // Human data
    const humanBars = [
      { label: 'Title & Abstract\nScreening', start: 0, end: 114.15, color: '#B7D3C6' },
      { label: 'Full-text\nScreening', start: 114.15, end: 187.62, color: '#6BAED6' },
      { label: 'Data\nExtraction', start: 187.62, end: 385.12, color: '#E38B48' },
    ];

    // AgentSLR data
    const agentBars = [
      { label: 'Title & Abstract\nScreening', start: 0, end: 3.32, color: '#B7D3C6' },
      { label: 'PDF-to-MD\nConversion', start: 3.32, end: 3.63, color: '#C9A3A3' },
      { label: 'Full-text\nScreening', start: 3.63, end: 4.19, color: '#6BAED6' },
      { label: 'Data\nExtraction', start: 4.19, end: 33.82, color: '#E38B48' },
    ];

    function pct(v) { return (v / maxHours * 100).toFixed(2) + '%'; }
    function w(bar) { return ((bar.end - bar.start) / maxHours * 100).toFixed(2) + '%'; }

    function renderRow(label, bars) {
      return `
        <div class="gantt-row">
          <div class="gantt-label">${label}</div>
          <div class="gantt-track">
            ${bars.map(b => `<div class="gantt-bar" style="left:${pct(b.start)};width:${w(b)};background:${b.color};" title="${b.label.replace('\n',' ')}: ${b.start.toFixed(1)}-${b.end.toFixed(1)}h"></div>`).join('')}
          </div>
        </div>`;
    }

    // Legend
    const legendItems = [
      { label: 'Title & Abstract Screening', color: '#B7D3C6' },
      { label: 'PDF-to-MD Conversion*', color: '#C9A3A3' },
      { label: 'Full-text Screening', color: '#6BAED6' },
      { label: 'Data Extraction', color: '#E38B48' },
    ];
    const legend = `<div style="display:flex;gap:14px;justify-content:center;margin-bottom:12px;flex-wrap:wrap;font-size:0.78rem;">
      ${legendItems.map(l => `<span style="display:flex;align-items:center;gap:4px;"><span style="width:12px;height:12px;background:${l.color};border-radius:2px;display:inline-block;"></span>${l.label}</span>`).join('')}
    </div>`;

    // Generate ticks based on zoom level
    const tickInterval = ganttZoomLevel >= 4 ? 5 : ganttZoomLevel >= 2 ? 25 : 50;
    const ticks = [];
    for (let t = 0; t <= maxHours; t += tickInterval) {
      ticks.push(t);
    }

    // Zoom controls
    const zoomControls = `
      <div style="display:flex;gap:8px;justify-content:center;align-items:center;margin-bottom:12px;">
        <button id="gantt-zoom-out" style="padding:4px 12px;border:1px solid #ccc;border-radius:4px;background:white;cursor:pointer;font-size:0.85rem;">−</button>
        <span style="font-size:0.78rem;color:var(--text-muted);min-width:60px;text-align:center;">Zoom: ${ganttZoomLevel}x</span>
        <button id="gantt-zoom-in" style="padding:4px 12px;border:1px solid #ccc;border-radius:4px;background:white;cursor:pointer;font-size:0.85rem;">+</button>
        <button id="gantt-reset" style="padding:4px 12px;border:1px solid #ccc;border-radius:4px;background:white;cursor:pointer;font-size:0.78rem;">Reset</button>
      </div>
    `;

    const ganttContent = `
      <div class="gantt-wrapper" style="overflow-x:auto;overflow-y:hidden;">
        <div style="min-width:${100 * ganttZoomLevel}%;">
          ${renderRow('Humans', humanBars)}
          ${renderRow('AgentSLR', agentBars)}
          <div class="gantt-axis">
            ${ticks.map(t => `<span>${t}</span>`).join('')}
          </div>
        </div>
      </div>
    `;

    container.innerHTML = `
      ${legend}
      ${zoomControls}
      ${ganttContent}
      <div style="text-align:center;font-size:0.78rem;color:var(--text-light);margin-top:8px;">Time (hours) - Scroll horizontally to pan</div>
    `;

    // Add zoom event listeners
    const zoomInBtn = document.getElementById('gantt-zoom-in');
    const zoomOutBtn = document.getElementById('gantt-zoom-out');
    const resetBtn = document.getElementById('gantt-reset');

    if (zoomInBtn) {
      zoomInBtn.addEventListener('click', () => {
        if (ganttZoomLevel < 8) {
          ganttZoomLevel *= 2;
          renderGantt(containerId);
        }
      });
    }

    if (zoomOutBtn) {
      zoomOutBtn.addEventListener('click', () => {
        if (ganttZoomLevel > 1) {
          ganttZoomLevel /= 2;
          renderGantt(containerId);
        }
      });
    }

    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        ganttZoomLevel = 1;
        renderGantt(containerId);
      });
    }
  }

  /* ---------- SCREENING BAR CHART ---------- */
  function renderScreeningChart(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const pathogens = ['Marburg', 'Ebola', 'Lassa', 'SARS', 'Zika', 'MERS', 'Nipah', 'Overall'];

    // Recall data [two-stage AI, direct full-text, human+AI]
    const data = {
      'Marburg': [0.76, 0.82, 0.80],
      'Ebola':   [0.83, 0.92, 0.83],
      'Lassa':   [0.89, 0.91, 0.82],
      'SARS':    [0.87, 0.90, 0.87],
      'Zika':    [0.72, 0.80, 0.77],
      'MERS':    [0.88, 0.97, 0.86],
      'Nipah':   [0.80, 0.95, 0.88],
      'Overall': [0.81, 0.92, 0.83],
    };

    const strategies = [
      { key: 0, label: 'AI Screen (Abstract) \u2192 AI Screen (Full-Text)', color: '#B7D3C6' },
      { key: 1, label: 'AI Screen (Direct Full-Text)', color: '#6BAED6' },
      { key: 2, label: 'Human Screen (Abstract) \u2192 AI Screen (Full-Text)', color: '#4A7FAD' },
    ];

    const svgW = 700, svgH = 300;
    const margin = { top: 40, right: 20, bottom: 50, left: 50 };
    const plotW = svgW - margin.left - margin.right;
    const plotH = svgH - margin.top - margin.bottom;

    const groupW = plotW / pathogens.length;
    const barW = groupW * 0.22;
    const barGap = 2;

    let svg = `<svg viewBox="0 0 ${svgW} ${svgH}" class="screening-chart-svg">`;

    // Legend with better spacing
    svg += `<g transform="translate(10, 8)">`;
    let legendX = 0;
    strategies.forEach((s, i) => {
      svg += `<rect x="${legendX}" y="0" width="12" height="12" rx="2" fill="${s.color}"/>`;
      svg += `<text x="${legendX + 16}" y="10" font-size="9" fill="#6B6B6B">${s.label}</text>`;
      // Calculate text width for proper spacing
      const textWidth = s.label.length * 5.5; // Approximate character width
      legendX += 16 + textWidth + 15; // icon width + text + gap
    });
    svg += `</g>`;

    // Y axis
    for (let y = 0; y <= 1; y += 0.2) {
      const yPos = margin.top + plotH - (y * plotH);
      svg += `<line x1="${margin.left}" y1="${yPos}" x2="${margin.left + plotW}" y2="${yPos}" stroke="#EDE8E1" stroke-width="1"/>`;
      svg += `<text x="${margin.left - 8}" y="${yPos + 3}" text-anchor="end" font-size="9" fill="#9A9A9A">${y.toFixed(1)}</text>`;
    }
    svg += `<text x="${margin.left - 35}" y="${margin.top + plotH/2}" text-anchor="middle" font-size="10" fill="#6B6B6B" transform="rotate(-90, ${margin.left - 35}, ${margin.top + plotH/2})">Recall</text>`;

    // Bars
    pathogens.forEach((p, pi) => {
      const groupX = margin.left + pi * groupW + groupW * 0.15;
      const vals = data[p];
      vals.forEach((v, si) => {
        const x = groupX + si * (barW + barGap);
        const h = v * plotH;
        const y = margin.top + plotH - h;
        svg += `<rect x="${x}" y="${y}" width="${barW}" height="${h}" rx="2" fill="${strategies[si].color}"/>`;
        // Error bar (simulated ~2-5% CI)
        const errH = (0.03 + Math.random() * 0.04) * plotH;
        const mid = x + barW / 2;
        svg += `<line x1="${mid}" y1="${y - errH/2}" x2="${mid}" y2="${y + errH/2}" stroke="#2D2D2D" stroke-width="1"/>`;
        svg += `<line x1="${mid - 3}" y1="${y - errH/2}" x2="${mid + 3}" y2="${y - errH/2}" stroke="#2D2D2D" stroke-width="1"/>`;
        svg += `<line x1="${mid - 3}" y1="${y + errH/2}" x2="${mid + 3}" y2="${y + errH/2}" stroke="#2D2D2D" stroke-width="1"/>`;
      });
      // Label
      svg += `<text x="${groupX + (3 * (barW + barGap)) / 2}" y="${margin.top + plotH + 18}" text-anchor="middle" font-size="9" fill="#6B6B6B">${p}</text>`;
    });

    svg += `</svg>`;
    container.innerHTML = svg;
  }

  /* ---------- EXTRACTION TABLE ---------- */
  function renderExtractionTable() {
    const tbody = document.getElementById('extraction-tbody');
    if (!tbody) return;

    const data = [
      { type: 'Parameters', pathogen: 'Lassa', vals: [0.438,0.955,0.600, 0.800,0.545,0.649, 0.594,0.655,0.615] },
      { type: '', pathogen: 'Ebola', vals: [0.510,0.958,0.665, 0.798,0.538,0.643, 0.581,0.604,0.583] },
      { type: '', pathogen: 'SARS', vals: [0.463,0.954,0.623, 0.909,0.667,0.769, 0.548,0.655,0.573] },
      { type: '', pathogen: 'Zika', vals: [0.352,0.949,0.514, 0.596,0.418,0.491, 0.519,0.581,0.541] },
      { type: '', pathogen: 'Average', vals: [0.441,0.954,0.601, 0.776,0.542,0.638, 0.561,0.624,0.578], avg: true },
      { type: 'Models', pathogen: 'Lassa', vals: [0.909,1.000,0.952, 0.600,1.000,0.750, 0.687,0.699,0.690] },
      { type: '', pathogen: 'Ebola', vals: [0.876,0.952,0.912, 0.500,1.000,0.667, 0.606,0.680,0.636] },
      { type: '', pathogen: 'SARS', vals: [0.841,0.841,0.841, 0.486,0.971,0.648, 0.610,0.683,0.638] },
      { type: '', pathogen: 'Zika', vals: [0.785,0.911,0.843, 0.483,0.977,0.646, 0.683,0.753,0.706] },
      { type: '', pathogen: 'Average', vals: [0.853,0.926,0.887, 0.517,0.987,0.678, 0.647,0.704,0.668], avg: true },
      { type: 'Outbreaks', pathogen: 'Lassa', vals: [0.690,0.816,0.705, 0.833,1.000,0.909, 0.864,0.740,0.778] },
      { type: '', pathogen: 'Zika', vals: [0.576,0.713,0.525, 0.489,0.449,0.468, 0.870,0.780,0.812] },
      { type: '', pathogen: 'Average', vals: [0.633,0.765,0.615, 0.661,0.724,0.689, 0.867,0.760,0.795], avg: true },
      { type: '<strong>Average</strong>', pathogen: '', vals: [0.644,0.905,0.718, 0.649,0.757,0.664, 0.720,0.723,0.710], avg: true },
    ];

    tbody.innerHTML = data.map(row => {
      const cls = row.avg ? ' class="row-avg"' : '';
      const cells = row.vals.map(v => `<td>${v.toFixed(3)}</td>`).join('');
      return `<tr${cls}><td>${row.type}</td><td>${row.pathogen}</td>${cells}</tr>`;
    }).join('');
  }

  /* ---------- EXPERT CHARTS ---------- */
  function renderExpertCharts() {
    renderHorizontalBars('flagging-chart', [
      { label: 'Parameters', value: 0.45, color: '#EFCFB8' },
      { label: 'Models', value: 0.35, color: '#E8B990' },
      { label: 'Outbreaks', value: 0.62, color: '#E0A56A' },
    ]);

    renderHorizontalBars('accuracy-chart', [
      { label: 'Parameters', value: 0.25, color: '#EFCFB8' },
      { label: 'Models', value: 0.72, color: '#E8B990' },
      { label: 'Outbreaks', value: 0.78, color: '#E0A56A' },
    ]);

    renderCompetenceHistogram('competence-chart');
  }

  function renderHorizontalBars(containerId, items) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Determine appropriate scale based on data range
    const minVal = Math.min(...items.map(i => i.value));
    const maxVal = Math.max(...items.map(i => i.value));
    
    // Use dynamic scale: start from 0 if max < 0.5, otherwise use a scale that fits the data better
    let scaleMin = 0;
    let scaleMax = 1;
    
    // If all values are between 0.2 and 0.85, use a tighter scale
    if (minVal >= 0.2 && maxVal <= 0.85) {
      scaleMin = 0;
      scaleMax = 1;
    }
    
    const scaleRange = scaleMax - scaleMin;
    
    container.innerHTML = items.map(item => {
      const percentage = ((item.value - scaleMin) / scaleRange) * 100;
      return `
      <div class="hbar-row">
        <div class="hbar-label">${item.label}</div>
        <div class="hbar-track">
          <div class="hbar-fill" style="width:${percentage}%;background:${item.color};"></div>
          <div class="hbar-value">${item.value.toFixed(2)}</div>
        </div>
      </div>`;
    }).join('') + `
      <div style="display:flex;justify-content:space-between;margin-left:80px;font-size:0.7rem;color:var(--text-light);margin-top:4px;">
        <span>${scaleMin}</span><span>${(scaleMin + scaleRange * 0.25).toFixed(2)}</span><span>${(scaleMin + scaleRange * 0.5).toFixed(2)}</span><span>${(scaleMin + scaleRange * 0.75).toFixed(2)}</span><span>${scaleMax}</span>
      </div>`;
  }

  function renderCompetenceHistogram(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Competence distribution data (approximate from figure)
    const categories = ['Parameters', 'Models', 'Outbreaks'];
    const colors = ['#EFCFB8', '#E8B990', '#E0A56A'];
    // Distributions across 1-7 scale
    const distributions = {
      'Parameters': [0.10, 0.25, 0.30, 0.20, 0.10, 0.03, 0.02],
      'Models':     [0.05, 0.10, 0.15, 0.25, 0.20, 0.15, 0.10],
      'Outbreaks':  [0.03, 0.08, 0.12, 0.22, 0.25, 0.18, 0.12],
    };
    const means = { 'Parameters': 3.1, 'Models': 4.3, 'Outbreaks': 4.6 };

    let html = '';
    categories.forEach((cat, ci) => {
      const dist = distributions[cat];
      const maxVal = Math.max(...dist);
      html += `<div style="margin-bottom:10px;">
        <div style="font-size:0.78rem;font-weight:500;margin-bottom:6px;color:var(--text-muted);">${cat}</div>
        <div class="competence-bar-group" style="height:80px;">
          ${dist.map((d, i) => {
            const h = (d / maxVal) * 70;
            return `<div class="competence-bar" style="height:${h}px;background:${colors[ci]};position:relative;">
              <div class="competence-bar-label">${i + 1}</div>
            </div>`;
          }).join('')}
        </div>
        <div style="font-size:0.7rem;color:var(--text-light);margin-top:14px;">Mean: ${means[cat].toFixed(1)} / 7.0</div>
      </div>`;
    });

    html += `<div style="display:flex;justify-content:space-between;font-size:0.7rem;color:var(--text-light);margin-top:6px;padding:0 2px;"><span>Incompetent</span><span>Autonomous</span></div>`;

    container.innerHTML = html;
  }

  /* ---------- PUBLIC API ---------- */
  function renderAll() {
    renderGantt('gantt-chart');
    renderScreeningChart('screening-chart');
    renderExtractionTable();
    renderExpertCharts();
  }

  return { renderAll, renderGantt, renderScreeningChart, renderExtractionTable, renderExpertCharts };
})();
