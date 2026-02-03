/* ======================================
   data.js — Data loading & CSV parsing
   ====================================== */

const DataLoader = (() => {
  // Simple CSV parser (handles quoted fields with commas)
  function parseCSV(text) {
    const lines = [];
    let current = '';
    let inQuote = false;
    for (let i = 0; i < text.length; i++) {
      const ch = text[i];
      if (ch === '"') {
        if (inQuote && text[i + 1] === '"') {
          current += '"';
          i++;
        } else {
          inQuote = !inQuote;
        }
      } else if (ch === '\n' && !inQuote) {
        lines.push(current);
        current = '';
      } else {
        current += ch;
      }
    }
    if (current.trim()) lines.push(current);

    if (lines.length === 0) return [];
    const headers = splitCSVLine(lines[0]);
    const rows = [];
    for (let i = 1; i < lines.length; i++) {
      const vals = splitCSVLine(lines[i]);
      if (vals.length === 0) continue;
      const obj = {};
      headers.forEach((h, idx) => { obj[h.trim()] = (vals[idx] || '').trim(); });
      rows.push(obj);
    }
    return rows;
  }

  function splitCSVLine(line) {
    const result = [];
    let current = '';
    let inQuote = false;
    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (ch === '"') {
        if (inQuote && line[i + 1] === '"') {
          current += '"';
          i++;
        } else {
          inQuote = !inQuote;
        }
      } else if (ch === ',' && !inQuote) {
        result.push(current);
        current = '';
      } else {
        current += ch;
      }
    }
    result.push(current);
    return result;
  }

  async function fetchCSV(path) {
    try {
      const resp = await fetch(path);
      if (!resp.ok) return [];
      const text = await resp.text();
      return parseCSV(text);
    } catch (e) {
      console.warn('Failed to load:', path, e);
      return [];
    }
  }

  async function fetchText(path) {
    try {
      const resp = await fetch(path);
      if (!resp.ok) return '';
      return await resp.text();
    } catch (e) {
      console.warn('Failed to load:', path, e);
      return '';
    }
  }

  // Load all data for a pathogen
  async function loadPathogenData(pathogen) {
    const base = `data/${pathogen}`;
    const [harvest, abstractScreen, fulltextScreen, models, outbreaks, parameters, modelsReport, outbreaksReport] = await Promise.all([
      fetchCSV(`${base}/harvests/metadata_with_downloads.csv`),
      fetchCSV(`${base}/screening/abstract_screening_results.csv`),
      fetchCSV(`${base}/screening/fulltext_screening_results.csv`),
      fetchCSV(`${base}/extractions/data_extraction_models.csv`),
      fetchCSV(`${base}/extractions/data_extraction_outbreaks.csv`),
      fetchCSV(`${base}/extractions/data_extraction_parameters.csv`),
      fetchText(`${base}/report/models/models_writeup.md`),
      fetchText(`${base}/report/outbreaks/outbreaks_writeup.md`),
    ]);

    return {
      harvest,
      abstractScreen,
      fulltextScreen,
      models,
      outbreaks,
      parameters,
      modelsReport,
      outbreaksReport,
    };
  }

  return { loadPathogenData, parseCSV, fetchCSV };
})();
