const xlsx = require('xlsx');
const fs = require('fs');

const COL = {
  L1: 0, L1_VAL: 1, L3: 4, L3_VAL: 5, L4: 6, L4_VAL: 7,
  SHOWS: 14, VISITS: 15, SPEND: 18, LEADS: 19, CPL: 21,
  CL_TAG: 22, CL_COUNT: 23, CL_PRICE: 24,
  SALES: 33, REVENUE: 34, ROAS: 37
};

function parseXlsx(filename) {
  const wb = xlsx.readFile(filename);
  const ws = wb.Sheets[wb.SheetNames[0]];
  const rows = xlsx.utils.sheet_to_json(ws, { header: 1 });
  return rows.slice(1).map(r => ({
    source: (r[COL.L1] || '').toString(),
    typeVal: (r[COL.L3_VAL] || '').toString(),
    campaign: (r[COL.L4] || '').toString(),
    campaignId: (r[COL.L4_VAL] || '').toString(),
    shows: parseInt(r[COL.SHOWS]) || 0,
    visits: parseInt(r[COL.VISITS]) || 0,
    spend: parseFloat(r[COL.SPEND]) || 0,
    leads: parseInt(r[COL.LEADS]) || 0,
    clCount: parseInt(r[COL.CL_COUNT]) || 0,
    clPrice: parseFloat(r[COL.CL_PRICE]) || 0,
    sales: parseInt(r[COL.SALES]) || 0,
    revenue: parseFloat(r[COL.REVENUE]) || 0,
    roas: parseFloat(r[COL.ROAS]) || 0
  })).filter(r => r.spend > 0 || r.leads > 0 || r.clCount > 0 || r.sales > 0);
}

function summarize(rows) {
  const ruqi = rows.filter(r => r.source.includes('ruqi'));
  const seq = rows.filter(r => r.source.includes('sequoiacervice'));

  function agg(arr) {
    const s = arr.reduce((a, r) => ({
      shows: a.shows + r.shows,
      visits: a.visits + r.visits,
      spend: a.spend + r.spend,
      leads: a.leads + r.leads,
      clCount: a.clCount + r.clCount,
      sales: a.sales + r.sales,
      revenue: a.revenue + r.revenue
    }), { shows: 0, visits: 0, spend: 0, leads: 0, clCount: 0, sales: 0, revenue: 0 });
    return {
      ...s,
      cpl: s.leads > 0 ? s.spend / s.leads : 0,
      clCpl: s.clCount > 0 ? s.spend / s.clCount : 0,
      cpo: s.sales > 0 ? s.spend / s.sales : 0,
      roas: s.spend > 0 ? s.revenue / s.spend : 0,
      leadCr: s.visits > 0 ? (s.leads / s.visits) * 100 : 0,
      clCr: s.visits > 0 ? (s.clCount / s.visits) * 100 : 0
    };
  }

  function byCampaign(arr) {
    const map = {};
    arr.forEach(r => {
      const key = `${r.campaign}|${r.campaignId}`;
      if (!map[key]) map[key] = { campaign: r.campaign, campaignId: r.campaignId, shows: 0, visits: 0, spend: 0, leads: 0, clCount: 0, sales: 0, revenue: 0 };
      map[key].shows += r.shows;
      map[key].visits += r.visits;
      map[key].spend += r.spend;
      map[key].leads += r.leads;
      map[key].clCount += r.clCount;
      map[key].sales += r.sales;
      map[key].revenue += r.revenue;
    });
    return Object.values(map).map(c => ({
      ...c,
      cpl: c.leads > 0 ? c.spend / c.leads : 0,
      clCpl: c.clCount > 0 ? c.spend / c.clCount : 0,
      cpo: c.sales > 0 ? c.spend / c.sales : 0,
      roas: c.spend > 0 ? c.revenue / c.spend : 0
    })).sort((a, b) => b.spend - a.spend);
  }

  return {
    ruqi: agg(ruqi),
    seq: agg(seq),
    total: agg(rows),
    ruqiCampaigns: byCampaign(ruqi),
    seqCampaigns: byCampaign(seq)
  };
}

const mayRows = parseXlsx('project_225433_report-17_2026-05-01-2026-05-31.xlsx');
const juneRows = parseXlsx('project_225433_report-17_2026-06-01-2026-06-15.xlsx');

const maySummary = summarize(mayRows);
const juneSummary = summarize(juneRows);

fs.writeFileSync('roistat_summary.json', JSON.stringify({ may: maySummary, june: juneSummary }, null, 2));
console.log('Saved roistat_summary.json');
console.log('May RUQI:', maySummary.ruqi);
console.log('June RUQI:', juneSummary.ruqi);
