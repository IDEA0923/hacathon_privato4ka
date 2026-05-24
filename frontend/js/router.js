const routes = {
  '/': `
    <section class="container">
      <div class="hero">
        <h1>Найди свою олимпиаду</h1>
        <p>
          Агрегатор всех российских олимпиад, конкурсов и научных конференций для школьников.
          Заполни профиль — получи персональный план участия на учебный год с дедлайнами
          и AI-обоснованиями выбора.
        </p>
        <a href="/profile" class="btn btn--primary btn--block-mobile" data-link>Начать →</a>
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
  '/profile': `
    <div class="container">
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
          <a href="/recommendations" class="btn btn--secondary" data-link>К рекомендациям →</a>
        </div>
      </form>
    </div>
  `,
  '/recommendations': `
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
  '/calendar': `
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
  `
};

const scripts = {
  '/profile': '/js/profile.js',
  '/recommendations': '/js/recommendations.js',
  '/calendar': '/js/calendar.js'
};

const navigate = (path) => {
  const app = document.getElementById('app');
  app.innerHTML = routes[path] || routes['/'];
  
  // Update active state in nav
  document.querySelectorAll('[data-link]').forEach(el => {
    el.classList.toggle('active', el.getAttribute('href') === path);
  });

  // Load page-specific script if needed
  if (scripts[path]) {
    const script = document.createElement('script');
    script.src = scripts[path];
    script.type = 'module';
    app.appendChild(script);
  }
};

document.addEventListener('click', e => {
  if (e.target.matches('[data-link]')) {
    e.preventDefault();
    const path = e.target.getAttribute('href');
    history.pushState(null, null, path);
    navigate(path);
  }
});

window.addEventListener('popstate', () => navigate(location.pathname));
navigate(location.pathname);
