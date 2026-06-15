const https = require('https');
const fs = require('fs');

const KEY = 'd894875529eb1a633bcc07f6b6785a84';
const PROJECT = '225433';

function get(path) {
  return new Promise(resolve => {
    const opts = {
      hostname: 'cloud.roistat.com',
      path,
      method: 'GET',
      headers: { 'Api-key': KEY }
    };
    const req = https.request(opts, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => resolve(d));
    });
    req.on('error', e => resolve('ERROR:' + e.message));
    req.end();
  });
}

async function fetchOrders(from, to) {
  let all = [];
  let offset = 0;
  const limit = 500;

  while (true) {
    const url = `/api/v1/project/integration/order/list?project=${PROJECT}&limit=${limit}&offset=${offset}&date_from=${from}&date_to=${to}`;
    const raw = await get(url);
    try {
      const data = JSON.parse(raw);
      const batch = data.data || [];
      all = all.concat(batch);
      if (batch.length < limit) break;
      offset += limit;
    } catch (e) {
      process.stderr.write(`Parse error: ${e.message}\n`);
      break;
    }
  }
  return all;
}

function isRuqi(o) {
  const page = (o.page || '').toLowerCase();
  const tags = o.custom_fields ? (o.custom_fields['Теги'] || '') : '';
  const company = o.custom_fields ? (o.custom_fields['НашаКомпания'] || '') : '';
  return page.includes('ruqi') ||
    tags.toLowerCase().includes('ruqi') ||
    company.toLowerCase().includes('руки') ||
    company.toLowerCase().includes('ruqi');
}

function getChannel(o) {
  const marker = o.roistat || '';
  const src = o.source_type || '';
  const visitSrc = o.visit ? (o.visit.source || {}) : {};
  const displayName = visitSrc.display_name || '';

  if (marker.startsWith('direct2_search')) return 'Директ — Поиск';
  if (marker.startsWith('direct2_context') || marker.startsWith('direct2_ad_network')) return 'Директ — РСЯ';
  if (marker.startsWith('direct')) return 'Директ';
  if (src === 'Calltouch') return 'Calltouch (звонок)';
  if (src === 'Tilda') return 'Tilda (форма)';
  if (src === 'Sipuni') return 'Sipuni (звонок)';
  if (displayName.includes('SEO') || displayName.includes('seo')) return 'SEO / Органика';
  if (displayName.includes('direct') || displayName.includes('Директ')) return 'Директ';
  if (marker && marker !== 'nosource-crm') return 'Roistat: ' + marker.split('_')[0];
  return 'Без источника';
}

function getCampaign(o) {
  // Try to extract campaign from page URL or custom fields
  const page = o.page || '';
  const utm = page.match(/utm_campaign=([^&]+)/);
  if (utm) {
    try { return decodeURIComponent(utm[1]); } catch (e) { return utm[1]; }
  }
  
  // From visit data if available
  if (o.visit && o.visit.source && o.visit.source.campaign) {
    return o.visit.source.campaign;
  }
  
  // From roistat marker
  const marker = o.roistat || '';
  if (marker.includes('_')) {
    const parts = marker.split('_');
    if (parts.length > 2) return parts.slice(2).join('_');
  }
  
  return 'Не определена';
}

async function main() {
  const from = '2026-05-01';
  const to = '2026-05-31';
  
  process.stderr.write(`Fetching Roistat orders ${from} to ${to}...\n`);
  const orders = await fetchOrders(from, to);
  process.stderr.write(`Total orders: ${orders.length}\n`);

  // Deduplicate
  const seen = new Set();
  const unique = orders.filter(o => {
    if (seen.has(o.id)) return false;
    seen.add(o.id);
    return true;
  });
  process.stderr.write(`After dedup: ${unique.length}\n`);

  // Filter RUQI
  const ruqi = unique.filter(isRuqi);
  process.stderr.write(`RUQI orders: ${ruqi.length}\n`);

  // Analysis
  const byStatus = {}, byChannel = {}, byCampaign = {}, byDay = {};
  let totalRevenue = 0;

  ruqi.forEach(o => {
    const st = o.status ? o.status.name : 'unknown';
    const stType = o.status ? o.status.type : 'unknown';
    byStatus[st] = (byStatus[st] || 0) + 1;

    const ch = getChannel(o);
    byChannel[ch] = (byChannel[ch] || 0) + 1;

    const camp = getCampaign(o);
    byCampaign[camp] = (byCampaign[camp] || 0) + 1;

    const day = (o.creation_date || '').substring(0, 10);
    if (!byDay[day]) byDay[day] = { count: 0, revenue: 0 };
    byDay[day].count++;
    byDay[day].revenue += parseFloat(o.revenue) || 0;

    totalRevenue += parseFloat(o.revenue) || 0;
  });

  const won = ruqi.filter(o => o.status && o.status.type === 'won');
  const fail = ruqi.filter(o => o.status && o.status.type === 'fail');
  const progress = ruqi.filter(o => o.status && o.status.type === 'progress');

  const result = {
    period: '2026-05-01 to 2026-05-31',
    totalOrders: unique.length,
    ruqiOrders: ruqi.length,
    won: won.length,
    fail: fail.length,
    progress: progress.length,
    conversionRate: ruqi.length > 0 ? ((won.length / ruqi.length) * 100).toFixed(1) : 0,
    totalRevenue: Math.round(totalRevenue / 100),
    byStatus,
    byChannel,
    byCampaign,
    byDay,
    details: ruqi.map(o => ({
      id: o.id,
      date: (o.creation_date || '').substring(0, 10),
      status: o.status ? o.status.name : 'unknown',
      statusType: o.status ? o.status.type : 'unknown',
      revenue: Math.round((parseFloat(o.revenue) || 0) / 100),
      channel: getChannel(o),
      campaign: getCampaign(o),
      page: (o.page || '').split('?')[0],
      source: o.source_type || 'unknown',
      roistat: o.roistat || '',
      tags: o.custom_fields ? (o.custom_fields['Теги'] || '') : ''
    }))
  };

  fs.writeFileSync('c:\\Users\\user\\Desktop\\kiro\\roistat_may_2026.json', JSON.stringify(result, null, 2));
  process.stderr.write('Saved to roistat_may_2026.json\n');

  console.log('\n========================================');
  console.log('ROISTAT RUQI — МАЙ 2026');
  console.log('========================================');
  console.log(`Всего заказов: ${unique.length}`);
  console.log(`RUQI заказов: ${ruqi.length}`);
  console.log(`WON: ${won.length} | FAIL: ${fail.length} | В работе: ${progress.length}`);
  console.log(`Конверсия: ${result.conversionRate}%`);
  console.log(`Выручка: ${result.totalRevenue.toLocaleString()} руб`);

  console.log('\n--- ПО КАНАЛАМ ---');
  Object.entries(byChannel).sort((a,b) => b[1]-a[1]).forEach(([k,v]) => console.log(`${v} | ${k}`));

  console.log('\n--- ПО КАМПАНИЯМ ---');
  Object.entries(byCampaign).sort((a,b) => b[1]-a[1]).slice(0, 20).forEach(([k,v]) => console.log(`${v} | ${k}`));

  console.log('\n--- ПО СТАТУСАМ ---');
  Object.entries(byStatus).sort((a,b) => b[1]-a[1]).forEach(([k,v]) => console.log(`${v} | ${k}`));
}

main().catch(e => {
  process.stderr.write('FATAL: ' + e.message + '\n');
  process.exit(1);
});
