const xlsx = require('xlsx');
const fs = require('fs');

const COL = {
  L1: 0, L1_VAL: 1,
  L2: 2, L2_VAL: 3,
  L3: 4, L3_VAL: 5,
  L4: 6, L4_VAL: 7,
  L5: 10, L5_VAL: 11,
  L6: 8, L6_VAL: 9,
  L7: 12, L7_VAL: 13,
  SHOWS: 14, VISITS: 15, CTR: 16, CPC: 17,
  SPEND: 18, LEADS: 19, CPL: 21,
  CL_TAG: 22, CL_COUNT: 23, CL_PRICE: 24, CL_CR: 25,
  POT_REV: 26, FORE_SALES: 27, FORE_CR: 28, FORE_REV: 29, FORE_CPO: 30,
  CPO: 31, SALES_CR: 32, SALES: 33, REVENUE: 34, AOV: 35, CYCLE: 36, ROAS: 37
};

function parseXlsx(filename) {
  const wb = xlsx.readFile(filename);
  const ws = wb.Sheets[wb.SheetNames[0]];
  const rows = xlsx.utils.sheet_to_json(ws, { header: 1 });
  return rows.slice(1).map(r => ({
    source: r[COL.L1] || '',
    sourceVal: r[COL.L1_VAL] || '',
    type: r[COL.L3] || '',
    typeVal: r[COL.L3_VAL] || '',
    campaign: r[COL.L4] || '',
    campaignId: r[COL.L4_VAL] || '',
    group: r[COL.L5] || '',
    groupId: r[COL.L5_VAL] || '',
    keyword: r[COL.L7] || '',
    keywordId: r[COL.L7_VAL] || '',
    shows: parseInt(r[COL.SHOWS]) || 0,
    visits: parseInt(r[COL.VISITS]) || 0,
    ctr: parseFloat(r[COL.CTR]) || 0,
    cpc: parseFloat(r[COL.CPC]) || 0,
    spend: parseFloat(r[COL.SPEND]) || 0,
    leads: parseInt(r[COL.LEADS]) || 0,
    cpl: parseFloat(r[COL.CPL]) || 0,
    clTag: r[COL.CL_TAG] || '',
    clCount: parseInt(r[COL.CL_COUNT]) || 0,
    clPrice: parseFloat(r[COL.CL_PRICE]) || 0,
    clCr: parseFloat(r[COL.CL_CR]) || 0,
    sales: parseInt(r[COL.SALES]) || 0,
    revenue: parseFloat(r[COL.REVENUE]) || 0,
    cpo: parseFloat(r[COL.CPO]) || 0,
    roas: parseFloat(r[COL.ROAS]) || 0,
    aov: parseFloat(r[COL.AOV]) || 0
  })).filter(r => r.spend > 0 || r.leads > 0 || r.clCount > 0 || r.sales > 0);
}

function aggregateByCampaign(rows) {
  const map = {};
  rows.forEach(r => {
    const key = `${r.source}|${r.campaign}|${r.campaignId}`;
    if (!map[key]) {
      map[key] = {
        source: r.source, campaign: r.campaign, campaignId: r.campaignId,
        shows: 0, visits: 0, spend: 0, leads: 0, clCount: 0, clPrice: 0,
        sales: 0, revenue: 0, groups: new Set(), keywords: new Set()
      };
    }
    map[key].shows += r.shows;
    map[key].visits += r.visits;
    map[key].spend += r.spend;
    map[key].leads += r.leads;
    map[key].clCount += r.clCount;
    if (r.clPrice > 0 && r.clCount > 0) {
      map[key].clPrice = (map[key].clPrice * (map[key].clCount - r.clCount) + r.clPrice * r.clCount) / map[key].clCount;
    }
    map[key].sales += r.sales;
    map[key].revenue += r.revenue;
    if (r.group) map[key].groups.add(r.group);
    if (r.keyword) map[key].keywords.add(r.keyword);
  });
  return Object.values(map).map(c => ({
    ...c,
    cpl: c.leads > 0 ? c.spend / c.leads : 0,
    clCpl: c.clCount > 0 ? c.spend / c.clCount : 0,
    cpo: c.sales > 0 ? c.spend / c.sales : 0,
    roas: c.spend > 0 ? c.revenue / c.spend : 0,
    leadCr: c.visits > 0 ? (c.leads / c.visits) * 100 : 0,
    clCr: c.visits > 0 ? (c.clCount / c.visits) * 100 : 0,
    salesCr: c.leads > 0 ? (c.sales / c.leads) * 100 : 0,
    groups: c.groups.size,
    keywords: c.keywords.size
  })).sort((a, b) => b.spend - a.spend);
}

function aggregateByGroup(rows) {
  const map = {};
  rows.forEach(r => {
    const key = `${r.source}|${r.campaign}|${r.group}|${r.groupId}`;
    if (!map[key]) {
      map[key] = {
        source: r.source, campaign: r.campaign, group: r.group, groupId: r.groupId,
        shows: 0, visits: 0, spend: 0, leads: 0, clCount: 0, sales: 0, revenue: 0, keywords: new Set()
      };
    }
    map[key].shows += r.shows;
    map[key].visits += r.visits;
    map[key].spend += r.spend;
    map[key].leads += r.leads;
    map[key].clCount += r.clCount;
    map[key].sales += r.sales;
    map[key].revenue += r.revenue;
    if (r.keyword) map[key].keywords.add(r.keyword);
  });
  return Object.values(map).map(g => ({
    ...g,
    cpl: g.leads > 0 ? g.spend / g.leads : 0,
    clCpl: g.clCount > 0 ? g.spend / g.clCount : 0,
    cpo: g.sales > 0 ? g.spend / g.sales : 0,
    roas: g.spend > 0 ? g.revenue / g.spend : 0,
    keywords: g.keywords.size
  })).sort((a, b) => b.spend - a.spend);
}

function aggregateTotals(rows) {
  const ruqi = rows.filter(r => r.source.includes('ruqi'));
  const seq = rows.filter(r => r.source.includes('sequoiacervice'));
  const ruqiSearch = ruqi.filter(r => r.typeVal === 'search');
  const ruqiContext = ruqi.filter(r => r.typeVal === 'context');
  const seqSearch = seq.filter(r => r.typeVal === 'search');
  const seqContext = seq.filter(r => r.typeVal === 'context');

  function sum(arr) {
    return {
      shows: arr.reduce((s, r) => s + r.shows, 0),
      visits: arr.reduce((s, r) => s + r.visits, 0),
      spend: arr.reduce((s, r) => s + r.spend, 0),
      leads: arr.reduce((s, r) => s + r.leads, 0),
      clCount: arr.reduce((s, r) => s + r.clCount, 0),
      sales: arr.reduce((s, r) => s + r.sales, 0),
      revenue: arr.reduce((s, r) => s + r.revenue, 0)
    };
  }

  function calc(t) {
    return {
      ...t,
      cpl: t.leads > 0 ? t.spend / t.leads : 0,
      clCpl: t.clCount > 0 ? t.spend / t.clCount : 0,
      cpo: t.sales > 0 ? t.spend / t.sales : 0,
      roas: t.spend > 0 ? t.revenue / t.spend : 0,
      leadCr: t.visits > 0 ? (t.leads / t.visits) * 100 : 0,
      clCr: t.visits > 0 ? (t.clCount / t.visits) * 100 : 0,
      salesCr: t.leads > 0 ? (t.sales / t.leads) * 100 : 0
    };
  }

  return {
    ruqi: calc(sum(ruqi)),
    seq: calc(sum(seq)),
    ruqiSearch: calc(sum(ruqiSearch)),
    ruqiContext: calc(sum(ruqiContext)),
    seqSearch: calc(sum(seqSearch)),
    seqContext: calc(sum(seqContext)),
    total: calc(sum(rows))
  };
}

function generateHTML(title, period, rows, filename) {
  const campaigns = aggregateByCampaign(rows);
  const groups = aggregateByGroup(rows);
  const totals = aggregateTotals(rows);

  const formatNum = (n, d = 0) => n ? n.toLocaleString('ru-RU', { minimumFractionDigits: d, maximumFractionDigits: d }) : '—';
  const formatMoney = (n) => n ? Math.round(n).toLocaleString('ru-RU') + ' ₽' : '—';

  const rowsHtml = campaigns.map((c, i) => `
    <tr>
      <td class="num">${i + 1}</td>
      <td class="name">${c.campaign}</td>
      <td class="num">${c.campaignId}</td>
      <td class="num">${formatNum(c.shows)}</td>
      <td class="num">${formatNum(c.visits)}</td>
      <td class="num">${formatNum(c.spend, 2)}</td>
      <td class="num">${formatNum(c.leads)}</td>
      <td class="num ${c.cpl > 5000 ? 'bad' : c.cpl < 2000 ? 'good' : ''}">${formatNum(c.cpl, 0)}</td>
      <td class="num ${c.clCpl > 10000 ? 'bad' : c.clCpl < 5000 ? 'good' : ''}">${formatNum(c.clCpl, 0)}</td>
      <td class="num">${formatNum(c.clCount)}</td>
      <td class="num">${formatNum(c.sales)}</td>
      <td class="num">${formatNum(c.revenue, 0)}</td>
      <td class="num ${c.roas > 3 ? 'good' : c.roas < 1 ? 'bad' : ''}">${formatNum(c.roas, 2)}</td>
      <td class="num">${c.groups}</td>
      <td class="num">${c.keywords}</td>
    </tr>
  `).join('');

  const groupsHtml = groups.slice(0, 50).map((g, i) => `
    <tr>
      <td class="num">${i + 1}</td>
      <td class="name">${g.campaign}</td>
      <td class="name">${g.group}</td>
      <td class="num">${formatNum(g.spend, 2)}</td>
      <td class="num">${formatNum(g.leads)}</td>
      <td class="num">${formatNum(g.clCount)}</td>
      <td class="num">${formatNum(g.sales)}</td>
      <td class="num">${formatNum(g.revenue, 0)}</td>
      <td class="num ${g.roas > 3 ? 'good' : g.roas < 1 ? 'bad' : ''}">${formatNum(g.roas, 2)}</td>
      <td class="num">${g.keywords}</td>
    </tr>
  `).join('');

  function kpiCard(label, t, color) {
    return `
    <div class="kpi ${color}">
      <div class="label">${label}</div>
      <div class="value">${formatMoney(t.spend)}</div>
      <div class="sub">${formatNum(t.leads)} заявок · ${formatNum(t.clCount)} ЦЛ · ${formatNum(t.sales)} продаж</div>
      <div class="sub">CPL ${formatNum(t.cpl, 0)} ₽ · ЦЛ ${formatNum(t.clCpl, 0)} ₽ · ROAS ${formatNum(t.roas, 2)}</div>
    </div>`;
  }

  const html = `<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${title}</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --bg: #0f111a; --surface: #161922; --surface2: #1e212e; --border: #2a2e3f;
  --accent: #6366f1; --green: #22c55e; --red: #ef4444; --yellow: #f59e0b; --blue: #3b82f6; --purple: #8b5cf6;
  --text: #e2e8f0; --muted: #94a3b8; --dim: #64748b;
}
body { background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 13px; }
.header { background: linear-gradient(135deg, #1e1b4b, #312e81); padding: 32px; }
.header-inner { max-width: 1400px; margin: 0 auto; }
.header h1 { font-size: 24px; font-weight: 800; background: linear-gradient(90deg, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.header .subtitle { color: var(--muted); margin-top: 6px; }
.header .updated { color: var(--dim); font-size: 12px; margin-top: 12px; background: rgba(255,255,255,0.05); display: inline-block; padding: 6px 14px; border-radius: 20px; }
.container { max-width: 1400px; margin: 0 auto; padding: 24px; }

.kpi-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-bottom: 24px; }
.kpi { background: var(--surface); border-radius: 14px; padding: 20px; border: 1px solid var(--border); }
.kpi .label { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
.kpi .value { font-size: 22px; font-weight: 800; color: var(--text); }
.kpi .sub { font-size: 12px; color: var(--dim); margin-top: 4px; }
.kpi.green { border-top: 3px solid var(--green); }
.kpi.blue { border-top: 3px solid var(--blue); }
.kpi.purple { border-top: 3px solid var(--purple); }
.kpi.yellow { border-top: 3px solid var(--yellow); }

.section-title { font-size: 16px; font-weight: 700; margin: 32px 0 16px; display: flex; align-items: center; gap: 10px; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: var(--accent); }

.table-wrap { background: var(--surface); border-radius: 14px; border: 1px solid var(--border); overflow: hidden; margin-bottom: 24px; overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 12px; min-width: 900px; }
thead { background: var(--surface2); position: sticky; top: 0; }
th { padding: 12px 10px; text-align: left; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: var(--muted); border-bottom: 1px solid var(--border); white-space: nowrap; }
td { padding: 10px; border-bottom: 1px solid var(--border); color: var(--text); }
tr:hover { background: rgba(255,255,255,0.02); }
.name { font-weight: 600; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.num { font-family: 'SF Mono', monospace; text-align: right; white-space: nowrap; }
.num.good { color: var(--green); font-weight: 700; }
.num.bad { color: var(--red); font-weight: 700; }
.num.yellow { color: var(--yellow); font-weight: 700; }

.tabs { display: flex; gap: 8px; margin-bottom: 16px; }
.tab { padding: 8px 16px; border-radius: 8px; font-size: 12px; font-weight: 600; cursor: pointer; background: var(--surface); border: 1px solid var(--border); color: var(--muted); }
.tab.active { background: var(--accent); color: white; border-color: var(--accent); }

.footer { text-align: center; color: var(--dim); font-size: 11px; padding: 40px 0; }

@media (max-width: 900px) { .kpi-row { grid-template-columns: 1fr; } }
</style>
</head>
<body>
<div class="header">
  <div class="header-inner">
    <h1>📊 Roistat — ${title}</h1>
    <div class="subtitle">Проект 225433 · Аналитика до уровня кампаний, групп и ключевых слов</div>
    <div class="updated">🕐 Период: ${period} · Данные из Roistat API</div>
  </div>
</div>
<div class="container">

  <div class="section-title"><span class="dot" style="background:#3b82f6"></span>Сводка по проектам</div>
  <div class="kpi-row">
    ${kpiCard('RUQI · Всего', totals.ruqi, 'blue')}
    ${kpiCard('RUQI · Поиск', totals.ruqiSearch, 'blue')}
    ${kpiCard('RUQI · РСЯ', totals.ruqiContext, 'blue')}
    ${kpiCard('Секвойя · Всего', totals.seq, 'purple')}
    ${kpiCard('Секвойя · Поиск', totals.seqSearch, 'purple')}
    ${kpiCard('Секвойя · РСЯ', totals.seqContext, 'purple')}
    ${kpiCard('ИТОГО', totals.total, 'green')}
  </div>

  <div class="section-title"><span class="dot" style="background:#22c55e"></span>Кампании (${campaigns.length} шт) — по убыванию расхода</div>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Кампания</th>
          <th>ID</th>
          <th>Показы</th>
          <th>Визиты</th>
          <th>Расход</th>
          <th>Заявки</th>
          <th>CPL</th>
          <th>ЦЛ ₽</th>
          <th>ЦЛ</th>
          <th>Продажи</th>
          <th>Выручка</th>
          <th>ROAS</th>
          <th>Групп</th>
          <th>Ключей</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHtml}
      </tbody>
    </table>
  </div>

  <div class="section-title"><span class="dot" style="background:#f59e0b"></span>Группы объявлений — Топ-50 по расходу</div>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Кампания</th>
          <th>Группа</th>
          <th>Расход</th>
          <th>Заявки</th>
          <th>ЦЛ</th>
          <th>Продажи</th>
          <th>Выручка</th>
          <th>ROAS</th>
          <th>Ключей</th>
        </tr>
      </thead>
      <tbody>
        ${groupsHtml}
      </tbody>
    </table>
  </div>

  <div class="footer">
    Данные из Roistat · Проект 225433 · ${period}
  </div>
</div>
</body>
</html>`;

  fs.writeFileSync(filename, html);
  console.log(`Generated ${filename} — ${campaigns.length} campaigns, ${groups.length} groups`);
}

// Parse both files
const mayRows = parseXlsx('project_225433_report-17_2026-05-01-2026-05-31.xlsx');
const juneRows = parseXlsx('project_225433_report-17_2026-06-01-2026-06-15.xlsx');

console.log(`May: ${mayRows.length} rows`);
console.log(`June: ${juneRows.length} rows`);

// Generate pages
generateHTML('Май 2026', '1–31 мая 2026', mayRows, 'roistat_may.html');
generateHTML('Июнь 2026 (1–15)', '1–15 июня 2026', juneRows, 'roistat_june.html');

console.log('\nDone! Files: roistat_may.html, roistat_june.html');
