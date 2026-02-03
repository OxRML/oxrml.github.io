/* ======================================
   app.js — Main application controller
   ====================================== */

document.addEventListener('DOMContentLoaded', () => {

  /* ---------- ELEMENTS ---------- */
  const select   = document.getElementById('pathogen-select');
  const runBtn   = document.getElementById('run-btn');
  const resetBtn = document.getElementById('reset-btn');
  const copyBtn  = document.getElementById('copy-bibtex');

  /* ---------- PATHOGEN SELECT ---------- */
  select.addEventListener('change', () => {
    runBtn.disabled = !select.value;
  });

  /* ---------- RUN PIPELINE ---------- */
  runBtn.addEventListener('click', async () => {
    const pathogen = select.value;
    if (!pathogen) return;

    runBtn.disabled = true;
    runBtn.textContent = 'Running...';
    resetBtn.style.display = 'inline-block';

    // Load data
    const data = await DataLoader.loadPathogenData(pathogen);

    if (!data.harvest.length && !data.abstractScreen.length) {
      // No data available for this pathogen yet
      alert(`Data for this pathogen is not yet available. Currently only Lassa fever data is included.`);
      runBtn.disabled = false;
      runBtn.textContent = 'Run Pipeline';
      return;
    }

    // Run animation
    await Pipeline.run(data);

    runBtn.textContent = 'Run Pipeline';
    runBtn.disabled = false;
  });

  /* ---------- RESET ---------- */
  resetBtn.addEventListener('click', () => {
    Pipeline.reset();
    resetBtn.style.display = 'none';
    runBtn.disabled = !select.value;
    runBtn.textContent = 'Run Pipeline';
  });

  /* ---------- CARD FLIP ---------- */
  document.querySelectorAll('.pipeline-card').forEach(card => {
    // Click front to flip (only when completed)
    card.querySelector('.card-front').addEventListener('click', (e) => {
      // Don't flip during animation or if not completed
      if (Pipeline.isRunning()) return;
      if (card.classList.contains('dimmed')) return;
      // Allow flip if completed or if pipeline hasn't run
      if (!card.classList.contains('active')) {
        card.classList.toggle('flipped');
      }
    });

    // Click back button to flip back
    const backBtn = card.querySelector('.flip-back-btn');
    if (backBtn) {
      backBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        card.classList.remove('flipped');
      });
    }
  });

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
