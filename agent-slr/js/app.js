/* ======================================
   app.js — Main application controller
   ====================================== */

document.addEventListener('DOMContentLoaded', () => {

  /* ---------- ELEMENTS ---------- */
  const copyBtn  = document.getElementById('copy-bibtex');
  const viewModelsMdBtn = document.getElementById('view-models-md');
  const viewOutbreaksMdBtn = document.getElementById('view-outbreaks-md');
  const mdModal = document.getElementById('md-modal');
  const mdModalTitle = document.getElementById('md-modal-title');
  const mdModalBody = document.getElementById('md-modal-body');
  const mdModalClose = document.getElementById('md-modal-close');
  const mdModalBackdrop = document.getElementById('md-modal-backdrop');
  const mdModalHeader = mdModal ? mdModal.querySelector('.md-modal-header') : null;
  let mdZoom = 1;

  function escapeHtml(str) {
    return (str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function resolveAssetPath(path, basePath) {
    if (!path) return '';
    const clean = path.trim();
    if (/^(https?:)?\/\//i.test(clean)) return clean;
    if (clean.startsWith('/')) return clean;
    if (clean.startsWith('data/pipeline/')) {
      let normalized = clean.replace(/^data\/pipeline\//, 'data/');
      normalized = normalized.replace(/(\/report\/(?:models|outbreaks))\/(fig\d+_[^/]+\.png)/, '$1/figures/$2');
      return normalized;
    }
    if (clean.startsWith('data/')) {
      return clean.replace(/(\/report\/(?:models|outbreaks))\/(fig\d+_[^/]+\.png)/, '$1/figures/$2');
    }
    return `${basePath}${clean.replace(/^\.\//, '')}`;
  }

  function renderMarkdown(md, basePath) {
    const lines = (md || '').replace(/\r\n/g, '\n').replace(/\r/g, '\n').split('\n');
    const html = [];

    function renderInline(text) {
      let out = escapeHtml((text || '').replace(/\\([*_`])/g, '$1'));
      out = out.replace(/`([^`]+)`/g, '<code>$1</code>');
      out = out.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
      out = out.replace(/(^|[\s>(])\*([^*\n]+)\*/g, '$1<em>$2</em>');
      out = out.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (m, label, href) => {
        const resolved = resolveAssetPath(href, basePath);
        return `<a href="${resolved}" target="_blank" rel="noopener noreferrer">${label}</a>`;
      });
      return out;
    }

    function parseFigureLayout(raw) {
      if (!raw) return '';
      const widthMatch = raw.match(/width_in\s*=\s*([0-9.]+)/i);
      const heightMatch = raw.match(/max_height_in\s*=\s*([0-9.]+)/i);
      const parts = [];
      if (widthMatch) parts.push(`max-width:min(100%, ${Math.round(parseFloat(widthMatch[1]) * 96)}px)`);
      if (heightMatch) parts.push(`max-height:${Math.round(parseFloat(heightMatch[1]) * 96)}px`);
      return parts.length ? ` style="${parts.join(';')}"` : '';
    }

    function isSeparatorRow(row) {
      return /^(\|?\s*:?-{3,}:?\s*)+\|?$/.test(row.trim());
    }

    let i = 0;
    while (i < lines.length) {
      const line = lines[i];
      const trimmed = line.trim();
      if (!trimmed) { i++; continue; }
      if (/^<!--[\s\S]*-->$/.test(trimmed)) { i++; continue; }

      if (trimmed.startsWith('```')) {
        const codeLines = [];
        i++;
        while (i < lines.length && !lines[i].trim().startsWith('```')) {
          codeLines.push(lines[i]);
          i++;
        }
        if (i < lines.length) i++;
        html.push(`<pre><code>${escapeHtml(codeLines.join('\n'))}</code></pre>`);
        continue;
      }

      const heading = trimmed.match(/^(#{1,6})\s+(.*)$/);
      if (heading) {
        const level = heading[1].length;
        html.push(`<h${level}>${renderInline(heading[2])}</h${level}>`);
        i++;
        continue;
      }

      if (/^-{3,}\s*$/.test(trimmed)) {
        html.push('<hr>');
        i++;
        continue;
      }

      const imgMatch = trimmed.match(/^!\[([^\]]*)\]\(([^)]+)\)\s*(?:<!--\s*fig-layout:\s*([^>]*)-->)?\s*$/);
      if (imgMatch) {
        const alt = imgMatch[1] || '';
        const src = resolveAssetPath(imgMatch[2], basePath);
        let layout = imgMatch[3] || '';
        let caption = '';
        if (!layout && i + 1 < lines.length) {
          const maybeLayout = lines[i + 1].trim().match(/^<!--\s*fig-layout:\s*([^>]*)-->$/);
          if (maybeLayout) {
            layout = maybeLayout[1] || '';
            i++;
          }
        }
        if (i + 1 < lines.length) {
          const maybeCaption = lines[i + 1].trim().match(/^\*(.+)\*$/);
          if (maybeCaption) {
            caption = maybeCaption[1];
            i++;
          }
        }
        html.push(`<figure><img src="${src}" alt="${escapeHtml(alt)}"${parseFigureLayout(layout)}>${caption || alt ? `<figcaption>${renderInline(caption || alt)}</figcaption>` : ''}</figure>`);
        i++;
        continue;
      }

      if (trimmed.startsWith('|') && i + 1 < lines.length && isSeparatorRow(lines[i + 1])) {
        const rowToCells = (row) => row.replace(/^\||\|$/g, '').split('|').map(cell => renderInline(cell.trim()));
        const headers = rowToCells(lines[i].trim());
        i += 2;
        const rows = [];
        while (i < lines.length && lines[i].trim().startsWith('|')) {
          rows.push(rowToCells(lines[i].trim()));
          i++;
        }
        html.push(`<table><thead><tr>${headers.map(cell => `<th>${cell}</th>`).join('')}</tr></thead><tbody>${rows.map(row => `<tr>${row.map(cell => `<td>${cell}</td>`).join('')}</tr>`).join('')}</tbody></table>`);
        continue;
      }

      if (trimmed.startsWith('>')) {
        const quoteLines = [];
        while (i < lines.length && lines[i].trim().startsWith('>')) {
          quoteLines.push(renderInline(lines[i].trim().replace(/^>\s?/, '')));
          i++;
        }
        html.push(`<blockquote>${quoteLines.join('<br>')}</blockquote>`);
        continue;
      }

      if (/^[-*]\s+/.test(trimmed)) {
        const items = [];
        while (i < lines.length && /^[-*]\s+/.test(lines[i].trim())) {
          items.push(`<li>${renderInline(lines[i].trim().replace(/^[-*]\s+/, ''))}</li>`);
          i++;
        }
        html.push(`<ul>${items.join('')}</ul>`);
        continue;
      }

      if (/^\d+\.\s+/.test(trimmed)) {
        const items = [];
        while (i < lines.length && /^\d+\.\s+/.test(lines[i].trim())) {
          items.push(`<li>${renderInline(lines[i].trim().replace(/^\d+\.\s+/, ''))}</li>`);
          i++;
        }
        html.push(`<ol>${items.join('')}</ol>`);
        continue;
      }

      const para = [renderInline(trimmed)];
      i++;
      while (i < lines.length && lines[i].trim() && !/^(#{1,6}\s+|```|[-*]\s+|\d+\.\s+|>|\||---+$|!\[|<!--)/.test(lines[i].trim())) {
        para.push(renderInline(lines[i].trim()));
        i++;
      }
      html.push(`<p>${para.join('<br>')}</p>`);
    }

    return html.join('\n');
  }

  function openMdModal(title, content, basePath) {
    if (!mdModal || !mdModalTitle || !mdModalBody) return;
    mdModalTitle.textContent = title;
    mdModalBody.innerHTML = renderMarkdown(content || 'No report content available.', basePath || '');
    mdModal.style.setProperty('--md-zoom', String(mdZoom));
    mdModal.classList.add('open');
    mdModal.setAttribute('aria-hidden', 'false');
  }

  function closeMdModal() {
    if (!mdModal) return;
    mdModal.classList.remove('open');
    mdModal.setAttribute('aria-hidden', 'true');
  }

  if (viewModelsMdBtn) {
    viewModelsMdBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      window.open(`md-viewer.html?path=${encodeURIComponent('data/lassa/report/models/models_writeup.md')}`, '_blank', 'noopener,noreferrer');
    });
  }

  if (viewOutbreaksMdBtn) {
    viewOutbreaksMdBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      window.open(`md-viewer.html?path=${encodeURIComponent('data/lassa/report/outbreaks/outbreaks_writeup.md')}`, '_blank', 'noopener,noreferrer');
    });
  }

  if (mdModalClose) mdModalClose.addEventListener('click', closeMdModal);
  if (mdModalBackdrop) mdModalBackdrop.addEventListener('click', closeMdModal);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeMdModal();
  });

  function setMdZoom(nextZoom) {
    if (!mdModal) return;
    mdZoom = Math.max(0.8, Math.min(1.6, Number(nextZoom.toFixed(2))));
    mdModal.style.setProperty('--md-zoom', String(mdZoom));
  }

  if (mdModalHeader && mdModalClose) {
    const zoomWrap = document.createElement('div');
    zoomWrap.className = 'md-modal-zoom';
    zoomWrap.innerHTML = `
      <button type="button" class="md-zoom-btn" id="md-zoom-out" title="Zoom out">A-</button>
      <button type="button" class="md-zoom-btn" id="md-zoom-reset" title="Reset zoom">100%</button>
      <button type="button" class="md-zoom-btn" id="md-zoom-in" title="Zoom in">A+</button>
    `;
    mdModalHeader.insertBefore(zoomWrap, mdModalClose);
    const zoomOutBtn = document.getElementById('md-zoom-out');
    const zoomInBtn = document.getElementById('md-zoom-in');
    const zoomResetBtn = document.getElementById('md-zoom-reset');
    if (zoomOutBtn) zoomOutBtn.addEventListener('click', () => setMdZoom(mdZoom - 0.1));
    if (zoomInBtn) zoomInBtn.addEventListener('click', () => setMdZoom(mdZoom + 0.1));
    if (zoomResetBtn) zoomResetBtn.addEventListener('click', () => setMdZoom(1));
  }

  /* ---------- COPY BIBTEX ---------- */
  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      const code = document.getElementById('bibtex-code');
      if (!code) return;
      navigator.clipboard.writeText(code.textContent).then(() => {
        copyBtn.textContent = 'Copied!';
        setTimeout(() => { copyBtn.textContent = 'Copy'; }, 2000);
      }).catch(() => {
        // Fallback
        const range = document.createRange();
        range.selectNode(code);
        window.getSelection().removeAllRanges();
        window.getSelection().addRange(range);
        document.execCommand('copy');
        copyBtn.textContent = 'Copied!';
        setTimeout(() => { copyBtn.textContent = 'Copy'; }, 2000);
      });
    });
  }

  /* ---------- RENDER CHARTS ---------- */
  Charts.renderAll();

  /* ---------- INTERSECTION OBSERVER for animations ---------- */
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.animationPlayState = 'running';
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.result-block').forEach(block => {
    block.style.animationPlayState = 'paused';
    observer.observe(block);
  });

});
