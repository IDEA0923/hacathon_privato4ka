import { Api } from './api.js';
import { $, el, clear, formatDate, deadlineLabel, skeletonCard } from './utils.js';
import { toast } from './notifications.js';

const list = $('#recommendations');
const subjectFilter = $('#filter-subject');
const levelFilter = $('#filter-level');
const resetBtn = $('#filter-reset');

let allItems = [];
let planIds = new Set();

async function init() {
  showSkeletons(6);

  // Параллельно: справочник предметов, рекомендации, текущий план
  const [subjects, recs, plan] = await Promise.all([
    Api.getSubjects(),
    Api.getRecommendations(),
    Api.getPlan(),
  ]);

  renderSubjectOptions(subjects);
  allItems = recs || [];
  planIds = new Set((plan || []).map(p => p.id));
  render();
}

function showSkeletons(n) {
  clear(list);
  for (let i = 0; i < n; i++) list.appendChild(skeletonCard());
}

function renderSubjectOptions(subjects) {
  subjects.forEach(s => {
    subjectFilter.appendChild(el('option', { text: s, attrs: { value: s } }));
  });
}

function applyFilters(items) {
  const sub = subjectFilter.value;
  const lvl = levelFilter.value;
  return items.filter(o => {
    if (sub && !o.subjects.includes(sub)) return false;
    if (lvl && String(o.level) !== lvl) return false;
    return true;
  });
}

function render() {
  const items = applyFilters(allItems);
  clear(list);

  if (!items.length) {
    list.appendChild(el('div', { class: 'empty', text: 'Под выбранные фильтры ничего не нашлось.' }));
    return;
  }

  items.forEach(o => list.appendChild(card(o)));
}

function card(o) {
  const inPlan = planIds.has(o.id);
  const scorePct = Math.round((o.score || 0) * 100);

  const reasonBox = el('div', { class: 'card__reason', style: { display: 'none' } });

  const explainBtn = el('button', { class: 'btn btn--ghost btn--sm', text: '💡 Почему мне?' });
  explainBtn.addEventListener('click', async () => {
    if (reasonBox.style.display === 'block') {
      reasonBox.style.display = 'none';
      return;
    }
    reasonBox.style.display = 'block';
    reasonBox.innerHTML = '<em class="muted">AI готовит обоснование...</em>';
    try {
      const res = await Api.explain(o.id);
      reasonBox.textContent = res.explanation || 'Обоснование недоступно.';
    } catch (err) {
      reasonBox.textContent = 'Не удалось получить обоснование: ' + err.message;
    }
  });

  const planBtn = el('button', {
    class: inPlan ? 'btn btn--secondary btn--sm' : 'btn btn--primary btn--sm',
    text: inPlan ? '✓ В плане' : '+ В план',
  });
  planBtn.addEventListener('click', async () => {
    planBtn.disabled = true;
    try {
      if (planIds.has(o.id)) {
        await Api.removeFromPlan(o.id);
        planIds.delete(o.id);
        planBtn.textContent = '+ В план';
        planBtn.className = 'btn btn--primary btn--sm';
        toast('Удалено из плана', o.title, 'info', 2500);
      } else {
        await Api.addToPlan(o.id);
        planIds.add(o.id);
        planBtn.textContent = '✓ В плане';
        planBtn.className = 'btn btn--secondary btn--sm';
        toast('Добавлено в план', o.title, 'success', 2500);
      }
    } catch (err) {
      toast('Ошибка', err.message, 'danger');
    } finally {
      planBtn.disabled = false;
    }
  });

  return el('div', { class: 'card' }, [
    el('div', { class: 'card__header' }, [
      el('h3', { class: 'card__title', text: o.title }),
      el('span', { class: `badge badge--level-${o.level}`, text: `${romanLevel(o.level)} ур.` }),
    ]),
    el('div', { class: 'card__meta' }, [
      el('span', { text: `📚 ${o.subjects.join(', ')}` }),
      el('span', { text: `🎓 ${formatGrades(o.grades)} класс` }),
      el('span', { text: `📅 ${deadlineLabel(o.deadline)}` }),
      o.stage && el('span', { text: `🏁 ${o.stage}` }),
    ]),
    o.tags?.length && el('div', { class: 'card__meta' },
      o.tags.map(t => el('span', { class: 'badge badge--score', text: t, style: { background: 'var(--color-surface-2)', color: 'var(--color-text-muted)' } }))
    ),
    el('div', { class: 'card__meta' }, [
      el('span', { text: `🎯 Релевантность: ${scorePct}%`, style: { color: 'var(--color-primary)', fontWeight: 600 } }),
    ]),
    reasonBox,
    el('div', { class: 'card__actions' }, [explainBtn, planBtn]),
  ]);
}

function romanLevel(l) {
  return ['', 'I', 'II', 'III'][l] || '?';
}

function formatGrades(grades) {
  if (!grades || !grades.length) return '—';
  if (grades.length === 1) return grades[0];
  return `${Math.min(...grades)}–${Math.max(...grades)}`;
}

subjectFilter.addEventListener('change', render);
levelFilter.addEventListener('change', render);
resetBtn.addEventListener('click', () => {
  subjectFilter.value = '';
  levelFilter.value = '';
  render();
});

init();
