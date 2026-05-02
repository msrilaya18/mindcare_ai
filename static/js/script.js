/* MindCare AI - Frontend Logic */

// Character counter
const textarea = document.getElementById('userInput');
const charCount = document.getElementById('charCount');

textarea.addEventListener('input', () => {
  const len = textarea.value.length;
  charCount.textContent = len;
  charCount.style.color = len > 900 ? '#ef4444' : len > 700 ? '#f59e0b' : '#64748b';
});

async function analyzeText() {
  const text = textarea.value.trim();

  if (!text) {
    showError('Please enter how you are feeling before analyzing.');
    return;
  }

  hideError();
  hideResult();
  setLoading(true);

  try {
    const response = await fetch('/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });

    const data = await response.json();

    if (!response.ok || data.error) {
      showError(data.error || 'An unexpected error occurred. Please try again.');
      return;
    }

    renderResult(data);
  } catch (err) {
    showError('Network error. Please check your connection and try again.');
  } finally {
    setLoading(false);
  }
}

function renderResult(data) {
  // Stress Banner & Mood Emoji
  const banner = document.getElementById('stressBanner');
  const stressValue = document.getElementById('stressValue');
  const moodEmoji = document.getElementById('moodEmoji');
  const level = (data.stress_level || 'LOW').toUpperCase();

  // Reset & Apply Classes
  banner.className = 'stress-banner mb-4 d-flex align-items-center justify-content-center gap-3';
  if (level === 'HIGH') {
    banner.style.background = 'rgba(239, 68, 68, 0.15)';
    banner.style.border = '1px solid rgba(239, 68, 68, 0.3)';
    stressValue.style.color = '#fca5a5';
  } else if (level === 'MEDIUM') {
    banner.style.background = 'rgba(245, 158, 11, 0.15)';
    banner.style.border = '1px solid rgba(245, 158, 11, 0.3)';
    stressValue.style.color = '#fcd34d';
  } else {
    banner.style.background = 'rgba(52, 211, 153, 0.15)';
    banner.style.border = '1px solid rgba(52, 211, 153, 0.3)';
    stressValue.style.color = '#6ee7b7';
  }

  stressValue.textContent = level;
  moodEmoji.textContent = data.mood_emoji || '🧠';

  // Affirmation
  document.getElementById('affirmationText').textContent = data.daily_affirmation || '';

  // Empathy
  document.getElementById('empathyText').textContent = data.empathy || '';

  // Next Step
  document.getElementById('nextStepText').textContent = data.next_step || 'Take a deep breath and relax.';

  // Tips
  const tipsList = document.getElementById('tipsList');
  tipsList.innerHTML = '';
  (data.tips || []).forEach((tip, i) => {
    const li = document.createElement('li');
    li.style.animationDelay = `${i * 0.08}s`;
    li.innerHTML = `<span class="tip-num">${i + 1}</span><span>${tip}</span>`;
    tipsList.appendChild(li);
  });

  // Helplines
  const helplines = document.getElementById('helplinesList');
  helplines.innerHTML = '';
  (data.helplines || []).forEach((h, i) => {
    const card = document.createElement('div');
    card.className = 'helpline-card';
    card.style.animationDelay = `${i * 0.1}s`;
    card.innerHTML = `
      <div class="helpline-name"><i class="bi bi-telephone-fill me-1"></i>${h.name}</div>
      <div class="helpline-number">${h.number}</div>
    `;
    helplines.appendChild(card);
  });

  document.getElementById('resultSection').classList.remove('d-none');

  // Smooth scroll to results
  setTimeout(() => {
    document.getElementById('resultSection').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 100);
}

function resetForm() {
  textarea.value = '';
  charCount.textContent = '0';
  hideResult();
  hideError();
  textarea.focus();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function setLoading(state) {
  const btn = document.getElementById('analyzeBtn');
  const btnText = btn.querySelector('.btn-text');
  const btnLoader = btn.querySelector('.btn-loader');
  btn.disabled = state;
  if (state) {
    btnText.classList.add('d-none');
    btnLoader.classList.remove('d-none');
  } else {
    btnText.classList.remove('d-none');
    btnLoader.classList.add('d-none');
  }
}

function showError(msg) {
  const el = document.getElementById('errorAlert');
  document.getElementById('errorText').textContent = msg;
  el.classList.remove('d-none');
}

function hideError() {
  document.getElementById('errorAlert').classList.add('d-none');
}

function hideResult() {
  document.getElementById('resultSection').classList.add('d-none');
}

// Allow Ctrl+Enter or Shift+Enter to submit
textarea.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.shiftKey) && e.key === 'Enter') {
    e.preventDefault();
    analyzeText();
  }
});
