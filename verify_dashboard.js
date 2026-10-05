/**
 * Проверка целостности данных дашборда.
 *   node verify_dashboard.js [index.html]
 *
 * Проверяет:
 *   1. JS-синтаксис встроенного <script> (нов Function(...)).
 *   2. Для каждой недели: сумма аккаунтов == итоги по показам/кликам/расходу/лидам/целевым.
 *   3. Лиды недели == Директ-лиды + SEO-лиды + Прочие (и то же по целевым).
 *   4. Производные метрики соответствуют формулам проекта (CPA = расход/лиды, CPL = расход/целевые).
 *   5. Каждый id недели уникален; months.weeks ссылаются на существующие недели.
 */

const fs = require('fs');
const path = require('path');

const file = process.argv[2] || path.join(__dirname, 'index.html');
const html = fs.readFileSync(file, 'utf8');

const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
const dataScript = scripts.find(s => s.includes('const weeks = ['));
if (!dataScript) {
  console.error('Не найден блок данных в', file);
  process.exit(1);
}

// 1. Синтаксис + вычисление констант.
// Блок данных содержит обращения к DOM (инициализация графиков), поэтому подменяем
// document/window/Chart заглушками — нам нужны только сами массивы данных.
const noop = () => {};
const universal = new Proxy(function () {}, {
  get(target, prop) {
    if (prop === Symbol.toPrimitive) return () => '';
    if (prop === 'length') return 0;
    if (prop === 'dataset' || prop === 'style' || prop === 'classList') return universal;
    return universal;
  },
  apply: () => universal,
  set: () => true,
});

let data;
try {
  const sandbox = `
    const document = {
      getElementById: () => universal,
      querySelectorAll: () => [],
      addEventListener: () => {},
    };
    const window = { setTimeout: () => {}, addEventListener: () => {} };
    const Chart = function () { return { destroy() {}, update() {}, options: {} }; };
    ${dataScript}
    return { weeks, months, monthDataOverrides, seoWeeklyData, weeklyDailyData };
  `;
  data = new Function('universal', sandbox)(universal);
} catch (err) {
  console.error('СИНТАКСИЧЕСКАЯ ОШИБКА в <script> данных:', err.message);
  process.exit(1);
}

const { weeks, months, monthDataOverrides, seoWeeklyData } = data;
const problems = [];
const warn = [];

const near = (a, b, tol = 0.02) => Math.abs(a - b) <= tol;

// 2 + 3. Целостность недель
for (const w of weeks) {
  const acc = Object.values(w.accounts || {});
  const imp = acc.reduce((s, a) => s + a.imp, 0);
  const clk = acc.reduce((s, a) => s + a.clicks, 0);
  const spend = acc.reduce((s, a) => s + a.spend, 0);
  const leads = acc.reduce((s, a) => s + (a.leads || 0), 0);
  const target = acc.reduce((s, a) => s + (a.target || 0), 0);

  if (imp !== w.impressions) problems.push(`${w.id}: показы ${w.impressions} ≠ Σ аккаунтов ${imp}`);
  if (clk !== w.clicks) problems.push(`${w.id}: клики ${w.clicks} ≠ Σ аккаунтов ${clk}`);
  if (!near(spend, w.spend)) problems.push(`${w.id}: расход ${w.spend} ≠ Σ аккаунтов ${spend.toFixed(2)}`);
  const channels = ['seoLeads', 'instagramLeads', 'otherLeads'];
  const channelTargets = ['seoTarget', 'instagramTarget', 'otherTarget'];
  const leadSum = leads + (w.seoLeads || 0) + (w.instagramLeads || 0) + (w.otherLeads || 0);
  const targetSum = target + (w.seoTarget || 0) + (w.instagramTarget || 0) + (w.otherTarget || 0);
  if (leadSum !== w.leads) {
    problems.push(`${w.id}: лиды ${w.leads} ≠ Директ ${leads} + ${channels.map(c => `${c} ${w[c] || 0}`).join(' + ')}`);
  }
  if (targetSum !== w.target) {
    problems.push(`${w.id}: целевые ${w.target} ≠ Директ ${target} + ${channelTargets.map(c => `${c} ${w[c] || 0}`).join(' + ')}`);
  }

  // 4. Производные метрики.
  // По конвенции проекта денежные метрики округляются до целых рублей,
  // проценты — до двух знаков. Поэтому допускаем именно такое округление.
  const exp = {
    ctr: { value: w.impressions ? (w.clicks / w.impressions * 100) : 0, kind: 'pct' },
    cpc: { value: w.clicks ? (w.spend / w.clicks) : 0, kind: 'rub' },
    cpa: { value: w.leads ? (w.spend / w.leads) : null, kind: 'rub' },
    cpl: { value: w.target ? (w.spend / w.target) : null, kind: 'rub' },
    convLead: { value: w.clicks ? (w.leads / w.clicks * 100) : 0, kind: 'pct' },
    convTarget: { value: w.leads ? (w.target / w.leads * 100) : 0, kind: 'pct' },
  };
  for (const [key, spec] of Object.entries(exp)) {
    const actual = w[key];
    if (spec.value === null) {
      if (actual !== null) problems.push(`${w.id}.${key}: ожидалось null, получено ${actual}`);
      continue;
    }
    const expected = spec.kind === 'rub' ? Math.round(spec.value) : Math.round(spec.value * 100) / 100;
    if (actual !== expected) {
      problems.push(`${w.id}.${key}: в файле ${actual}, по формуле ${spec.value.toFixed(2)} -> округление даёт ${expected}`);
    }
  }
}

// 5. Уникальность и ссылки месяцев
const ids = weeks.map(w => w.id);
const dupes = ids.filter((id, i) => ids.indexOf(id) !== i);
if (dupes.length) problems.push(`Дубликаты id недель: ${[...new Set(dupes)].join(', ')}`);

for (const m of months) {
  for (const id of m.weeks) {
    if (!ids.includes(id)) problems.push(`Месяц ${m.id} ссылается на несуществующую неделю ${id}`);
  }
  const twice = months.flatMap(x => x.weeks).filter((id, i, arr) => arr.indexOf(id) !== i);
  if (twice.includes(m.weeks[0]) && months.filter(x => x.weeks.includes(m.weeks[0])).length > 1) {
    problems.push(`Неделя ${m.weeks[0]} числится в нескольких месяцах`);
  }
  if (m.weeks.length && !m.weeks.every(id => ids.includes(id))) {
    warn.push(`Месяц ${m.id}: недели ${m.weeks.join(', ')}`);
  }
}

// Месячные снапшоты
for (const [id, mo] of Object.entries(monthDataOverrides || {})) {
  const acc = Object.values(mo.accounts || {});
  const imp = acc.reduce((s, a) => s + a.imp, 0);
  if (imp !== mo.impressions) problems.push(`monthDataOverrides[${id}]: показы ${mo.impressions} ≠ Σ аккаунтов ${imp}`);
}

// SEO: неделя без seoWeeklyData или с расхождением visits.
// Для ранних недель (w1–w12) значения в weeks[] и в seoWeeklyData расходятся исторически,
// поэтому это предупреждение, а не ошибка.
for (const w of weeks) {
  const entry = seoWeeklyData[w.id];
  if (!entry) {
    if (w.seo) warn.push(`${w.id}: seo=${w.seo}, но нет записи в seoWeeklyData (SEO-блок будет пустым)`);
    continue;
  }
  if (entry.stats && entry.stats.visits !== w.seo) {
    warn.push(`${w.id}: seo в weeks[] = ${w.seo}, в seoWeeklyData.stats.visits = ${entry.stats.visits}`);
  }
}

console.log(`Проверено недель: ${weeks.length}, месяцев: ${months.length}`);
if (warn.length) {
  console.log('\nПредупреждения:');
  warn.forEach(w => console.log('  ~ ' + w));
}
if (problems.length) {
  console.log('\nОШИБКИ:');
  problems.forEach(p => console.log('  ✗ ' + p));
  process.exit(1);
}
console.log('\nВсе проверки пройдены ✓');
