// Инициализация Telegram WebApp SDK + общая мобильная навигация.
// Безопасна вне Telegram — там tg === undefined, всё дегрейдится тихо.

const tg = window.Telegram?.WebApp;

export function initTelegram() {
  if (!tg) return null;
  try {
    tg.ready();
    tg.expand();
    // На свежих клиентах — на весь экран
    if (typeof tg.requestFullscreen === 'function') {
      try { tg.requestFullscreen(); } catch (_) {}
    }
    // Цвет хедера/фона под тему мини-приложения
    if (typeof tg.setHeaderColor === 'function') {
      try { tg.setHeaderColor('secondary_bg_color'); } catch (_) {}
    }
    if (typeof tg.disableVerticalSwipes === 'function') {
      try { tg.disableVerticalSwipes(); } catch (_) {}
    }
  } catch (e) {
    console.warn('TG init failed', e);
  }
  return tg;
}

// Системная BackButton в шапке Telegram
export function setupBackButton() {
  if (!tg?.BackButton) return;
  // На главной кнопку прячем, на остальных страницах — показываем
  const isHome = location.pathname === '/' || location.pathname.endsWith('/index.html');
  if (isHome) {
    tg.BackButton.hide();
  } else {
    tg.BackButton.show();
    tg.BackButton.onClick(() => {
      if (history.length > 1) history.back();
      else location.href = '/';
    });
  }
}

// Лёгкая тактильная отдача (если есть)
export function haptic(type = 'light') {
  try { tg?.HapticFeedback?.impactOccurred?.(type); } catch (_) {}
}

// Помечает активный пункт нижней навигации по текущему пути
export function highlightActiveTab() {
  const path = location.pathname.replace(/\/$/, '') || '/';
  document.querySelectorAll('.tabbar__item').forEach(a => {
    const href = a.getAttribute('href') || '';
    const norm = href.replace(/\/$/, '') || '/';
    const isActive =
      norm === path ||
      (norm === '/' && (path === '' || path === '/index.html')) ||
      (norm !== '/' && path.endsWith(norm));
    a.classList.toggle('tabbar__item--active', isActive);
  });
}

// Автостарт при импорте модуля
initTelegram();
setupBackButton();
document.addEventListener('DOMContentLoaded', highlightActiveTab);
