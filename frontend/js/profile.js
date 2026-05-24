import { Api } from './api.js';
import { $, el, clear } from './utils.js';
import { toast } from './notifications.js';

const form = $('#profile-form');
const subjectsBox = $('#subjects');
const regionSelect = $('#region');

let selectedSubjects = new Set();

async function init() {
  // Загружаем справочники
  const [regions, subjects] = await Promise.all([
    Api.getRegions(),
    Api.getSubjects(),
  ]);

  renderRegions(regions);
  renderSubjects(subjects);

  // Подтягиваем сохранённый профиль
  const profile = await Api.getProfile();
  if (profile) fillForm(profile);
}

function renderRegions(regions) {
  clear(regionSelect);
  regionSelect.appendChild(el('option', { text: '— выберите —', attrs: { value: '' } }));
  regions.forEach(r => regionSelect.appendChild(el('option', { text: r, attrs: { value: r } })));
}

function renderSubjects(subjects) {
  clear(subjectsBox);
  subjects.forEach(s => {
    const chip = el('label', { class: 'chip' }, [
      el('input', { attrs: { type: 'checkbox', value: s } }),
      s,
    ]);
    const input = chip.querySelector('input');
    input.addEventListener('change', () => {
      if (input.checked) {
        selectedSubjects.add(s);
        chip.classList.add('chip--active');
      } else {
        selectedSubjects.delete(s);
        chip.classList.remove('chip--active');
      }
    });
    subjectsBox.appendChild(chip);
  });
}

function fillForm(p) {
  if (p.name) $('#name').value = p.name;
  if (p.grade) $('#grade').value = p.grade;
  if (p.region) $('#region').value = p.region;
  if (p.level) $('#level').value = p.level;
  if (p.past) $('#past').value = p.past;
  if (Array.isArray(p.subjects)) {
    p.subjects.forEach(s => {
      const input = subjectsBox.querySelector(`input[value="${s}"]`);
      if (input) {
        input.checked = true;
        input.dispatchEvent(new Event('change'));
      }
    });
  }
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  if (selectedSubjects.size === 0) {
    toast('Выберите хотя бы один предмет', '', 'warning');
    return;
  }

  const data = {
    name: $('#name').value.trim(),
    grade: Number($('#grade').value),
    region: $('#region').value,
    level: $('#level').value,
    past: $('#past').value.trim(),
    subjects: Array.from(selectedSubjects),
  };

  const btn = form.querySelector('button[type="submit"]');
  btn.disabled = true;
  btn.textContent = 'Сохраняем...';

  try {
    await Api.saveProfile(data);
    toast('Профиль сохранён', 'Переходим к рекомендациям...', 'success', 2000);
    setTimeout(() => { window.location.href = '/recommendations.html'; }, 800);
  } catch (err) {
    toast('Ошибка сохранения', err.message, 'danger');
    btn.disabled = false;
    btn.textContent = 'Сохранить и продолжить';
  }
});

init();
