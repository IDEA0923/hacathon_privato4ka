// Модуль общения с бэкендом
// Все запросы идут на /api/... — Nginx проксирует на C++ сервер (backend:8080)

const API_BASE = '/api';

// Получение/установка user_id (упрощённая авторизация для прототипа)
export const Auth = {
  getUserId() {
    let id = localStorage.getItem('user_id');
    if (!id) {
      id = 'u_' + Math.random().toString(36).slice(2, 10);
      localStorage.setItem('user_id', id);
    }
    return id;
  },
  reset() {
    localStorage.removeItem('user_id');
    localStorage.removeItem('profile');
  },
};

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const opts = {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  };
  if (opts.body && typeof opts.body !== 'string') {
    opts.body = JSON.stringify(opts.body);
  }

  try {
    const res = await fetch(url, opts);
    if (!res.ok) {
      const text = await res.text().catch(() => '');
      throw new Error(`API ${res.status}: ${text || res.statusText}`);
    }
    if (res.status === 204) return null;
    return await res.json();
  } catch (err) {
    console.error(`[API] ${endpoint}`, err);
    throw err;
  }
}

export const Api = {
  // Профиль
  saveProfile(profile) {
    return request('/profile', { method: 'POST', body: { user_id: Auth.getUserId(), ...profile } });
  },
  getProfile() {
    return request(`/profile?user_id=${Auth.getUserId()}`);
  },

  // Рекомендации
  getRecommendations(filters = {}) {
    const params = new URLSearchParams({ user_id: Auth.getUserId(), ...filters });
    return request(`/recommendations?${params}`);
  },
  explain(olympiadId) {
    return request(`/explain?user_id=${Auth.getUserId()}&olympiad_id=${olympiadId}`);
  },

  // План
  addToPlan(olympiadId) {
    return request('/plan', { method: 'POST', body: { user_id: Auth.getUserId(), olympiad_id: olympiadId } });
  },
  getPlan() {
    return request(`/plan?user_id=${Auth.getUserId()}`);
  },
  removeFromPlan(olympiadId) {
    return request(`/plan?user_id=${Auth.getUserId()}&olympiad_id=${olympiadId}`, { method: 'DELETE' });
  },

  // Оповещения
  getNotifications() {
    return request(`/notifications?user_id=${Auth.getUserId()}`);
  },

  // Справочники
  getRegions() { return request('/regions'); },
  getSubjects() { return request('/subjects'); },
};

// ===== MOCK-режим =====
// Проект — frontend-only (мини-приложение Telegram). Бэкенда нет.
// Принудительно включаем mock при загрузке модуля — все вызовы Api идут в локальные данные.
try { localStorage.setItem('mock', '1'); } catch (_) {}
const MOCK_OLYMPIADS = [
  {
    id: 1, title: 'Всероссийская олимпиада по математике',
    subjects: ['математика'], level: 1, grades: [9, 10, 11],
    region: 'all', deadline: '2025-10-15', stage: 'школьный этап',
    score: 0.95, tags: ['РСОШ', 'диплом → льготы при поступлении'],
  },
  {
    id: 2, title: 'Олимпиада «Ломоносов» — физика',
    subjects: ['физика'], level: 1, grades: [10, 11],
    region: 'all', deadline: '2025-11-20', stage: 'отборочный тур',
    score: 0.88, tags: ['МГУ', 'РСОШ'],
  },
  {
    id: 3, title: 'Турнир Эйлера (математика)',
    subjects: ['математика'], level: 2, grades: [8],
    region: 'all', deadline: '2025-12-05', stage: 'дистанционный тур',
    score: 0.82, tags: ['8 класс', 'подготовка к ВсОШ'],
  },
  {
    id: 4, title: 'Открытая олимпиада по информатике (Иннополис)',
    subjects: ['информатика'], level: 2, grades: [9, 10, 11],
    region: 'all', deadline: '2025-10-30', stage: 'онлайн-отбор',
    score: 0.79, tags: ['программирование', 'РСОШ'],
  },
  {
    id: 5, title: 'Олимпиада «Высшая проба» — обществознание',
    subjects: ['обществознание'], level: 1, grades: [10, 11],
    region: 'all', deadline: '2025-11-10', stage: 'отборочный',
    score: 0.74, tags: ['НИУ ВШЭ', 'РСОШ'],
  },
  {
    id: 6, title: 'Региональный конкурс «Юный исследователь»',
    subjects: ['биология', 'химия'], level: 3, grades: [7, 8, 9],
    region: 'Приморский край', deadline: '2026-02-15', stage: 'заочный',
    score: 0.68, tags: ['проектная работа', 'регион'],
  },
];

const MOCK_REGIONS = [
  'Москва', 'Санкт-Петербург', 'Приморский край', 'Хабаровский край',
  'Республика Татарстан', 'Новосибирская область', 'Свердловская область',
  'Краснодарский край', 'Республика Башкортостан', 'Все регионы',
];

const MOCK_SUBJECTS = [
  'математика', 'физика', 'информатика', 'химия', 'биология',
  'русский язык', 'литература', 'английский язык', 'история',
  'обществознание', 'география', 'экономика',
];

const MOCK_REASONS = {
  1: 'У вас указан углублённый уровень по математике и 10 класс — ВсОШ это базовая траектория к диплому, дающему льготы БВИ при поступлении в любой вуз России.',
  2: 'Олимпиада «Ломоносов» входит в перечень РСОШ I уровня. Для вас (физика, 10–11 класс, продвинутый уровень) это шанс получить 100 баллов ЕГЭ или БВИ в МГУ.',
  3: 'Турнир Эйлера специально для 8 класса — это прямая подготовка к будущим этапам ВсОШ по математике. Уровень II РСОШ.',
  4: 'Информатика + олимпиадное программирование. Открытая олимпиада Иннополиса даёт льготы в технических вузах и подходит под ваш профиль.',
  5: 'Для гуманитарного трека «Высшая проба» — топовый выбор: РСОШ I уровня, диплом даёт БВИ в НИУ ВШЭ.',
  6: 'Региональный конкурс под ваш регион. Низкий порог входа, хорошо подходит для накопления опыта в 7–9 классах.',
};

function mockEnabled() {
  return localStorage.getItem('mock') === '1';
}

export function enableMock() {
  localStorage.setItem('mock', '1');
}

// Автоматический переключатель: если API падает, поднимаем мок и кэшируем
const original = { ...Api };

Api.getProfile = async () => {
  if (mockEnabled()) return JSON.parse(localStorage.getItem('profile') || 'null');
  try { return await original.getProfile(); }
  catch { enableMock(); return JSON.parse(localStorage.getItem('profile') || 'null'); }
};

Api.saveProfile = async (profile) => {
  if (mockEnabled()) {
    localStorage.setItem('profile', JSON.stringify(profile));
    return { ok: true };
  }
  try {
    const r = await original.saveProfile(profile);
    localStorage.setItem('profile', JSON.stringify(profile));
    return r;
  } catch {
    enableMock();
    localStorage.setItem('profile', JSON.stringify(profile));
    return { ok: true };
  }
};

Api.getRecommendations = async (filters = {}) => {
  if (mockEnabled()) return mockRecommend(filters);
  try { return await original.getRecommendations(filters); }
  catch { enableMock(); return mockRecommend(filters); }
};

Api.explain = async (id) => {
  if (mockEnabled()) {
    await new Promise(r => setTimeout(r, 700));
    return { explanation: MOCK_REASONS[id] || 'Эта олимпиада подходит под ваш профиль по предметам и классу.' };
  }
  try { return await original.explain(id); }
  catch { enableMock(); return Api.explain(id); }
};

Api.getPlan = async () => {
  if (mockEnabled()) {
    const ids = JSON.parse(localStorage.getItem('plan') || '[]');
    return MOCK_OLYMPIADS.filter(o => ids.includes(o.id));
  }
  try { return await original.getPlan(); }
  catch { enableMock(); return Api.getPlan(); }
};

Api.addToPlan = async (id) => {
  if (mockEnabled()) {
    const ids = JSON.parse(localStorage.getItem('plan') || '[]');
    if (!ids.includes(id)) ids.push(id);
    localStorage.setItem('plan', JSON.stringify(ids));
    return { ok: true };
  }
  try { return await original.addToPlan(id); }
  catch { enableMock(); return Api.addToPlan(id); }
};

Api.removeFromPlan = async (id) => {
  if (mockEnabled()) {
    const ids = JSON.parse(localStorage.getItem('plan') || '[]').filter(x => x !== id);
    localStorage.setItem('plan', JSON.stringify(ids));
    return { ok: true };
  }
  try { return await original.removeFromPlan(id); }
  catch { enableMock(); return Api.removeFromPlan(id); }
};

Api.getNotifications = async () => {
  if (mockEnabled()) {
    const plan = await Api.getPlan();
    const now = new Date();
    return plan
      .map(o => ({ ...o, daysLeft: Math.ceil((new Date(o.deadline) - now) / 86400000) }))
      .filter(o => o.daysLeft >= 0 && o.daysLeft <= 14);
  }
  try { return await original.getNotifications(); }
  catch { enableMock(); return Api.getNotifications(); }
};

Api.getRegions = async () => {
  if (mockEnabled()) return MOCK_REGIONS;
  try { return await original.getRegions(); }
  catch { enableMock(); return MOCK_REGIONS; }
};

Api.getSubjects = async () => {
  if (mockEnabled()) return MOCK_SUBJECTS;
  try { return await original.getSubjects(); }
  catch { enableMock(); return MOCK_SUBJECTS; }
};

function mockRecommend(filters) {
  const profile = JSON.parse(localStorage.getItem('profile') || '{}');
  let list = [...MOCK_OLYMPIADS];

  // Фильтр по предмету
  if (filters.subject) {
    list = list.filter(o => o.subjects.includes(filters.subject));
  }
  // Фильтр по уровню
  if (filters.level) {
    list = list.filter(o => String(o.level) === String(filters.level));
  }
  // Релевантность под профиль
  if (profile.subjects?.length) {
    list = list.map(o => {
      const overlap = o.subjects.filter(s => profile.subjects.includes(s)).length;
      const gradeMatch = profile.grade && o.grades.includes(Number(profile.grade)) ? 0.2 : 0;
      return { ...o, score: Math.min(1, o.score * 0.5 + overlap * 0.25 + gradeMatch) };
    });
  }
  return list.sort((a, b) => b.score - a.score);
}
