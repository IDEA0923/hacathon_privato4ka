// Хэш-роутер для SPA: маршруты вида #/profile, #/recommendations, #/calendar.
// Работает без nginx и без серверного try_files — годится для python http.server,
// `serve`, локального открытия и т.п.
//
// Принципы:
// 1. HTML каждой страницы — это шаблон-строка ниже (один index.html на весь сайт).
// 2. Скрипт страницы импортируется один раз через dynamic import() и кэшируется.
//    Затем при каждом входе на маршрут мы дёргаем у него init() — это позволяет
//    повторно «оживить» страницу после возврата (модули браузер повторно не
//    исполняет, поэтому без явного init() ничего бы не произошло).
// 3. Клик по <a data-link href="#/..."> перехватывается и меняет location.hash.

const routes = {
  '/': {
    title: 'AI-рекрутер олимпиад',
    html: `
    <section class="container">
      <div class="hero">
        <h1>Найди свою олимпиаду</h1>
        <p>
          Агрегатор всех российских олимпиад, конкурсов и научных конференций для школьников.
          Заполни профиль — получи персональный план участия на учебный год с дедлайнами
          и AI-обоснованиями выбора.
        </p>
        <a href="#/profile" class="btn btn--primary btn--block-mobile" data-link>Начать →</a>
      </div>

      <div class="features">
        <div class="feature">
          <div class="feature__icon">📚</div>
          <h3>Все источники</h3>
          <p class="muted">РСОШ, перечень Минпросвещения, региональные реестры — собираем в одном месте.</p>
        </div>
        <div class="feature">
          <div class="feature__icon">🎯</div>
          <h3>Персональные рекомендации</h3>
          <p class="muted">Подбор по предметам, классу, региону и уровню подготовки.</p>
        </div>
        <div class="feature">
          <div class="feature__icon">🤖</div>
          <h3>AI-обоснования</h3>
          <p class="muted">LLM объясняет: почему именно эта олимпиада подходит именно тебе.</p>
        </div>
        <div class="feature">
          <div class="feature__icon">📅</div>
          <h3>Календарь дедлайнов</h3>
          <p class="muted">Все ключевые даты в одном месте + умные оповещения.</p>
        </div>
      </div>
    </section>
  `,
  },
  '/profile': {
    title: 'Профиль — AI-рекрутер олимпиад',
    module: () => import('./profile.js'),
    html: `    <div class="container">
      <h1>Профиль школьника</h1>
      <p class="muted" style="margin-bottom: 24px;">
        Заполни анкету — мы подберём олимпиады под твой профиль.
      </p>

      <form id="profile-form" class="form">
        <div class="form__group">
          <label class="form__label" for="name">ФИО</label>
          <input type="text" id="name" name="name" class="form__input" placeholder="Иванов Иван Иванович" required />
        </div>

        <div class="form__group">
          <label class="form__label" for="grade">Класс</label>
          <select id="grade" name="grade" class="form__select" required>
            <option value="">— выберите —</option>
            <option value="5">5</option>
            <option value="6">6</option>
            <option value="7">7</option>
            <option value="8">8</option>
            <option value="9">9</option>
            <option value="10">10</option>
            <option value="11">11</option>
          </select>
        </div>

        <div class="form__group">
          <label class="form__label" for="region">Регион</label>
          <select id="region" name="region" class="form__select" required>
            <option value="">Загрузка...</option>
          </select>
        </div>

        <div class="form__group">
          <label class="form__label">Предметы (выберите несколько)</label>
          <div id="subjects" class="chips"></div>
          <p class="form__hint">Можно выбрать любое количество.</p>
        </div>

        <div class="form__group">
          <label class="form__label" for="level">Уровень подготовки</label>
          <select id="level" name="level" class="form__select" required>
            <option value="">— выберите —</option>
            <option value="beginner">Начальный — пробую впервые</option>
            <option value="intermediate">Средний — участвовал в школьных этапах</option>
            <option value="advanced">Продвинутый — призёр / победитель</option>
          </select>
        </div>

        <div class="form__group">
          <label class="form__label" for="past">Прошлые олимпиады (опционально)</label>
          <textarea id="past" name="past" class="form__textarea" rows="3"
            placeholder="Например: призёр ВсОШ по математике, 9 класс"></textarea>        </div>

        <div class="form__actions">
          <button type="submit" class="btn btn--primary">Сохранить и продолжить</button>
          <a href="#/recommendations" class="btn btn--secondary" data-link>К рекомендациям →</a>
        </div>
      </form>
    </div>
  `,
  },
  '/recommendations': {    title: 'Рекомендации — AI-рекрутер олимпиад',
    module: () => import('./recommendations.js'),
    html: `
    <div class="container">
      <h1>Подобрано для вас</h1>
      <p class="muted" style="margin-bottom: 24px;">
        Олимпиады отсортированы по релевантности вашему профилю.
      </p>

      <div class="filters">
        <select id="filter-subject" class="form__select filters__select">
          <option value="">Все предметы</option>
        </select>
        <select id="filter-level" class="form__select filters__select">
          <option value="">Все уровни</option>
          <option value="1">I уровень</option>
          <option value="2">II уровень</option>
          <option value="3">III уровень</option>
        </select>
        <button id="filter-reset" class="btn btn--ghost btn--sm">Сбросить</button>
      </div>

      <div id="recommendations" class="cards"></div>
    </div>
  `,
  },
  '/calendar': {
    title: 'Календарь — AI-рекрутер олимпиад',
    module: () => import('./calendar.js'),
    html: `
    <div class="container">
      <div class="page-head">
        <div>
          <h1 class="page-head__title">Календарь дедлайнов</h1>
          <p class="muted">Все ключевые даты по олимпиадам в вашем плане.</p>
        </div>
        <button id="export-ics" class="btn btn--secondary">📥 Экспорт в .ics</button>
      </div>

      <div id="calendar" class="calendar"></div>
    </div>
  `,
  },
};

function currentPath() {
  // location.hash имеет вид '#/profile' либо пустой. Нормализуем к '/...'.
  const raw = location.hash.replace(/^#/, '');
  if (!raw || raw === '/') return '/';
  return raw;
}

function updateActive(path) {
  document.querySelectorAll('[data-link]').forEach((el) => {
    const href = el.getAttribute('href') || '';
    const linkPath = href.replace(/^#/, '');
    const isActive =
      linkPath === path ||
      (linkPath === '/' && (path === '' || path === '/'));
    el.classList.toggle('active', isActive);
    if (el.classList.contains('tabbar__item')) {
      el.classList.toggle('tabbar__item--active', isActive);
    }
  });
}

async function navigate() {
  const path = currentPath();
  const route = routes[path] || routes['/'];

  const app = document.getElementById('app');
  if (!app) return;

  app.innerHTML = route.html;
  if (route.title) document.title = route.title;
  updateActive(path);
  window.scrollTo(0, 0);

  if (route.module) {
    try {
      const mod = await route.module();
      // Модуль страницы исполняется только один раз; для повторных заходов
      // дёргаем экспортируемую init() — она навешивает обработчики и
      // запускает запросы (с авто-fallback на mock внутри Api.*).
      if (typeof mod.init === 'function') {
        mod.init();
      }
    } catch (err) {
      console.error('[router] failed to load page module:', err);
    }
  }
}

// Перехватываем клики по data-link с hash-ссылками.
document.addEventListener('click', (e) => {
  const link = e.target.closest && e.target.closest('[data-link]');
  if (!link) return;
  const href = link.getAttribute('href') || '';
  if (!href.startsWith('#')) return;
  e.preventDefault();
  if (location.hash === href) {
    // Тот же маршрут — всё равно перезапустим init().
    navigate();
  } else {
    location.hash = href;
  }
});

window.addEventListener('hashchange', navigate);

// Программная навигация для других модулей (например, форма профиля).
export function goTo(path) {
  const hash = path.startsWith('#')
    ? path
    : '#' + (path.startsWith('/') ? path : '/' + path);
  if (location.hash === hash) navigate();
  else location.hash = hash;
}

// Стартовая навигация.
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', navigate);
} else {
  navigate();
}
