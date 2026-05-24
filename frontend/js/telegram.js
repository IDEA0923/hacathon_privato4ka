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

// Системная BackButton в шапке Telegram.
// SPA работает на хэш-роутере, поэтому ориентируемся на location.hash,
// а не на pathname, и обновляем состояние на каждый hashchange.
export function setupBackButton() {
  if (!tg?.BackButton) return;

  const isHomeHash = () => {
    const h = location.hash.replace(/^#/, '');
    return !h || h === '/' || h === '/index.html';
  };

  // Кнопку привязываем один раз — поведение универсальное.
  try {
    tg.BackButton.onClick(() => {
      if (!isHomeHash() && history.length > 1) {
        history.back();
      } else {
        // На главной просто прячем кнопку.
        location.hash = '#/';
      }
    });
  } catch (_) {}

  const sync = () => {
    try {
      if (isHomeHash()) tg.BackButton.hide();
      else tg.BackButton.show();
    } catch (_) {}
  };

  sync();
  window.addEventListener('hashchange', sync);
}
// Лёгкая тактильная отдача (если есть)
export function haptic(type = 'light') {
  try { tg?.HapticFeedback?.impactOccurred?.(type); } catch (_) {}
}

// Подсветка активной вкладки в нижней навигации теперь полностью
// делается хэш-роутером (см. router.js → updateActive), поэтому
// отдельный обработчик тут больше не нужен.

// Автостарт при импорте модуля
initTelegram();
setupBackButton();
