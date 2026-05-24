// Утилиты: даты, шаблоны, DOM-хелперы

export const MONTHS_GENITIVE = [
  'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
  'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря',
];

export const MONTHS_NOMINATIVE = [
  'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
  'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь',
];

export const MONTHS_SHORT = ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек'];

export function formatDate(iso) {
  const d = new Date(iso);
  if (isNaN(d)) return iso;
  return `${d.getDate()} ${MONTHS_GENITIVE[d.getMonth()]} ${d.getFullYear()}`;
}

export function daysLeft(iso) {
  const diff = new Date(iso) - new Date();
  return Math.ceil(diff / 86400000);
}

export function deadlineLabel(iso) {
  const d = daysLeft(iso);
  if (d < 0) return 'просрочено';
  if (d === 0) return 'сегодня';
  if (d === 1) return 'завтра';
  if (d <= 7) return `через ${d} дн.`;
  return formatDate(iso);
}

// Создание DOM-элемента по тегу + опции
export function el(tag, opts = {}, children = []) {
  const node = document.createElement(tag);
  if (opts.class) node.className = opts.class;
  if (opts.text != null) node.textContent = opts.text;
  if (opts.html != null) node.innerHTML = opts.html;
  if (opts.attrs) for (const [k, v] of Object.entries(opts.attrs)) node.setAttribute(k, v);
  if (opts.on) for (const [evt, fn] of Object.entries(opts.on)) node.addEventListener(evt, fn);
  if (opts.style) Object.assign(node.style, opts.style);
  for (const child of [].concat(children)) {
    if (child == null || child === false) continue;
    node.appendChild(typeof child === 'string' ? document.createTextNode(child) : child);
  }
  return node;
}

export function $(selector, root = document) {
  return root.querySelector(selector);
}

export function $$(selector, root = document) {
  return Array.from(root.querySelectorAll(selector));
}

export function clear(node) {
  while (node.firstChild) node.removeChild(node.firstChild);
}

// Группировка олимпиад по месяцу дедлайна
export function groupByMonth(items, dateField = 'deadline') {
  const map = new Map();
  for (const it of items) {
    const d = new Date(it[dateField]);
    if (isNaN(d)) continue;
    const key = `${d.getFullYear()}-${String(d.getMonth()).padStart(2, '0')}`;
    if (!map.has(key)) map.set(key, { year: d.getFullYear(), month: d.getMonth(), items: [] });
    map.get(key).items.push(it);
  }
  return Array.from(map.values()).sort((a, b) => a.year - b.year || a.month - b.month);
}

// Debounce
export function debounce(fn, ms = 300) {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), ms);
  };
}

// Скелетоны
export function skeletonCard() {
  return el('div', { class: 'card' }, [
    el('div', { class: 'skeleton', style: { width: '60%', height: '20px' } }),
    el('div', { class: 'skeleton', style: { width: '40%', marginTop: '8px' } }),
    el('div', { class: 'skeleton', style: { width: '100%', height: '60px', marginTop: '12px' } }),
  ]);
}
