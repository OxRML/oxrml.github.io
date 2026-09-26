/* ======================================
   app.js — Main application controller
   ====================================== */

document.addEventListener('DOMContentLoaded', () => {
  const copyBtn = document.getElementById('copy-bibtex');

  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      const code = document.getElementById('bibtex-code');
      if (!code) return;

      navigator.clipboard.writeText(code.textContent).then(() => {
        copyBtn.textContent = 'Copied!';
        setTimeout(() => { copyBtn.textContent = 'Copy'; }, 2000);
      }).catch(() => {
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

  Charts.renderAll();

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.animationPlayState = 'running';
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.result-block').forEach((block) => {
    block.style.animationPlayState = 'paused';
    observer.observe(block);
  });
});
