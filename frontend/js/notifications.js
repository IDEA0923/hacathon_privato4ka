// Toast-уведомления + проверка ближайших дедлайнов

import { Api } from './api.js';
import { el, deadlineLabel } from './utils.js';

function ensureContainer() {
  let c = document.querySelector('.toasts');
  if (!c) {
    c = el('div', { class: 'toasts' });
    document.body.appendChild(c);
  }
  return c;
}

export function toast(title, body = '', type = 'info', ttl = 5000) {
  const c = ensureContainer();
  const node = el('div', { class: `toast toast--${type}` }, [
    el('div', { class: 'toast__title', text: title }),
    body && el('div', { class: 'toast__body', text: body }),
  ]);
  c.appendChild(node);
  setTimeout(() => {
    node.style.transition = 'opacity 0.3s';
    node.style.opacity = '0';
    setTimeout(() => node.remove(), 300);
  }, ttl);
}

export async function checkUpcoming() {
  try {
    const items = await Api.getNotifications();
    if (!items || !items.length) return;

    // Показываем максимум 3 ближайших
    items.slice(0, 3).forEach(o => {
      const days = o.daysLeft ?? null;
      const type = days != null && days <= 3 ? 'warning' : 'info';
      toast(o.title, `Дедлайн: ${deadlineLabel(o.deadline)}`, type, 7000);
    });
  } catch (e) {
    console.warn('Не удалось проверить дедлайны', e);
  }
}
