import { Api } from './api.js';
import { $, el, clear, groupByMonth, formatDate, deadlineLabel, MONTHS_NOMINATIVE, MONTHS_SHORT } from './utils.js';
import { toast } from './notifications.js';

const root = $('#calendar');
const exportBtn = $('#export-ics');

async function init() {
  clear(root);
  root.appendChild(el('div', { class: 'loading', text: 'Загружаем ваш план...' }));

  try {
    const plan = await Api.getPlan();
    render(plan || []);
  } catch (err) {
    clear(root);
    root.appendChild(el('div', { class: 'empty', text: 'Не удалось загрузить план: ' + err.message }));
  }
}

function render(items) {
  clear(root);

  if (!items.length) {
    root.appendChild(el('div', { class: 'empty' }, [
      el('h3', { text: 'План пока пуст' }),
      el('p', { class: 'muted', text: 'Перейдите в раздел «Рекомендации» и добавьте интересующие олимпиады.' }),
      el('a', { class: 'btn btn--primary', attrs: { href: '/recommendations.html' }, text: 'К рекомендациям →', style: { marginTop: '16px', display: 'inline-block' } }),
    ]));
    return;
  }

  const months = groupByMonth(items, 'deadline');
  months.forEach(m => root.appendChild(monthBlock(m)));
}

function monthBlock(m) {
  return el('div', { class: 'month' }, [
    el('h2', { class: 'month__title', text: `${MONTHS_NOMINATIVE[m.month]} ${m.year}` }),
    ...m.items
      .sort((a, b) => new Date(a.deadline) - new Date(b.deadline))
      .map(eventRow),
  ]);
}

function eventRow(o) {
  const d = new Date(o.deadline);

  const removeBtn = el('button', { class: 'btn btn--ghost btn--sm', text: '🗑' });
  removeBtn.addEventListener('click', async () => {
    if (!confirm(`Удалить «${o.title}» из плана?`)) return;
    try {
      await Api.removeFromPlan(o.id);
      toast('Удалено из плана', o.title, 'info', 2500);
      init();
    } catch (err) {
      toast('Ошибка', err.message, 'danger');
    }
  });

  return el('div', { class: 'event' }, [
    el('div', { class: 'event__date' }, [
      el('div', { class: 'event__date-day', text: d.getDate() }),
      el('div', { class: 'event__date-month', text: MONTHS_SHORT[d.getMonth()] }),
    ]),
    el('div', { class: 'event__body' }, [
      el('div', { class: 'event__title', text: o.title }),
      el('div', { class: 'event__sub', text: `${o.subjects?.join(', ') || ''} · ${o.stage || 'дедлайн'} · ${deadlineLabel(o.deadline)}` }),
    ]),
    removeBtn,
  ]);
}

// ===== Экспорт в .ics =====
function buildIcs(items) {
  const lines = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//AI-recruiter//Olympiads//RU',
    'CALSCALE:GREGORIAN',
  ];

  items.forEach(o => {
    const d = new Date(o.deadline);
    const dateStr = `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, '0')}${String(d.getDate()).padStart(2, '0')}`;
    const uid = `olymp-${o.id}@ai-recruiter`;
    const summary = (o.title || '').replace(/[\n,;]/g, ' ');
    const desc = `Предметы: ${(o.subjects || []).join(', ')}. Этап: ${o.stage || '—'}.`.replace(/[\n,;]/g, ' ');

    lines.push(
      'BEGIN:VEVENT',
      `UID:${uid}`,
      `DTSTAMP:${dateStr}T090000Z`,
      `DTSTART;VALUE=DATE:${dateStr}`,
      `SUMMARY:${summary}`,
      `DESCRIPTION:${desc}`,
      'END:VEVENT'
    );
  });

  lines.push('END:VCALENDAR');
  return lines.join('\r\n');
}

exportBtn.addEventListener('click', async () => {
  try {
    const plan = await Api.getPlan();
    if (!plan || !plan.length) {
      toast('План пуст', 'Добавьте олимпиады в рекомендациях.', 'warning');
      return;
    }
    const ics = buildIcs(plan);
    const blob = new Blob([ics], { type: 'text/calendar' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'olympiads.ics';
    a.click();
    URL.revokeObjectURL(url);
    toast('Готово', 'Файл olympiads.ics скачан.', 'success');
  } catch (err) {
    toast('Ошибка экспорта', err.message, 'danger');
  }
});

init();
