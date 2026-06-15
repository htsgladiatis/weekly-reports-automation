const https = require('https');

const ACCOUNTS = [
  { label: 'RUQI', token: 'y0__xCJkPzcBRijg0AgrJW_gBdA2r0WSmm50ZSBl2-JK2R4wNZozg' },
  { label: 'SEQUOIA', token: 'y0__xCWk628BBijg0Ags_nyjhfdsbSqn6kSthlGE4XfkitZgndWJQ' }
];

function getCampaigns(token, label) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      method: 'get',
      params: {
        SelectionCriteria: {},
        FieldNames: ['Id', 'Name', 'State', 'Status', 'Type', 'DailyBudget', 'Funds']
      }
    });

    const options = {
      hostname: 'api.direct.yandex.com',
      path: '/json/v5/campaigns',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json; charset=utf-8',
        'Accept-Language': 'ru',
        'Content-Length': Buffer.byteLength(body)
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          resolve({ label, data: json });
        } catch (e) {
          resolve({ label, raw: data });
        }
      });
    });

    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

(async () => {
  for (const acc of ACCOUNTS) {
    const result = await getCampaigns(acc.token, acc.label);
    console.log(`\n=== ${result.label} ===`);
    if (result.data && result.data.result && result.data.result.Campaigns) {
      const camps = result.data.result.Campaigns;
      console.log(`Всего кампаний: ${camps.length}`);
      camps.forEach(c => {
        const state = c.State || '?';
        const status = c.Status || '?';
        const daily = c.DailyBudget ? `${c.DailyBudget.Amount/1000000}₽` : '-';
        const funds = c.Funds ? `${c.Funds.Mode}` : '-';
        console.log(`${c.Id}\t${c.Name}\t${state}\t${status}\t${daily}\t${funds}`);
      });
    } else {
      console.log('ERROR:', result.raw || result.data);
    }
  }
})();
