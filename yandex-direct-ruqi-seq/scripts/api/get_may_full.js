const https = require('https');

const CALLS = [
  {
    label: 'RUQI',
    token: 'y0__xCJkPzcBRijg0AgrJW_gBdA2r0WSmm50ZSBl2-JK2R4wNZozg',
    reportName: 'MayFull_Ruqi_' + Date.now()
  },
  {
    label: 'SEQUOIA',
    token: 'y0__xCWk628BBijg0Ags_nyjhfdsbSqn6kSthlGE4XfkitZgndWJQ',
    reportName: 'MayFull_Seq_' + Date.now()
  }
];

function makeRequest(token, reportName) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      method: 'get',
      params: {
        SelectionCriteria: { DateFrom: '2026-05-01', DateTo: '2026-05-31' },
        FieldNames: ['CampaignId', 'CampaignName', 'Cost', 'Impressions', 'Clicks', 'Conversions'],
        ReportName: reportName,
        ReportType: 'CAMPAIGN_PERFORMANCE_REPORT',
        DateRangeType: 'CUSTOM_DATE',
        Format: 'TSV',
        IncludeVAT: 'YES',
        IncludeDiscount: 'NO'
      }
    });

    const options = {
      hostname: 'api.direct.yandex.com',
      path: '/json/v5/reports',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json; charset=utf-8',
        'Accept-Language': 'ru',
        'processingMode': 'auto',
        'returnMoneyInMicros': 'false',
        'Content-Length': Buffer.byteLength(body)
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        resolve({ status: res.statusCode, headers: res.headers, body: data });
      });
    });

    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

async function fetchReport(label, token, reportName) {
  console.log(`\n=== ${label} — fetching report: ${reportName} ===`);
  let attempt = 0;
  const maxAttempts = 20;
  const retryDelay = 5000;

  while (attempt < maxAttempts) {
    attempt++;
    console.log(`Attempt ${attempt}...`);
    const result = await makeRequest(token, reportName);
    console.log(`HTTP ${result.status}`);

    if (result.status === 200) {
      console.log(`SUCCESS — got TSV data`);
      return result.body;
    } else if (result.status === 201 || result.status === 202) {
      const retryIn = result.headers['retryIn'] || result.headers['retryin'] || retryDelay / 1000;
      console.log(`Report not ready (${result.status}), retrying in ${retryIn}s...`);
      await new Promise(r => setTimeout(r, Math.max(Number(retryIn) * 1000, retryDelay)));
    } else {
      console.error(`ERROR ${result.status}:`);
      console.error(result.body);
      return `ERROR ${result.status}:\n${result.body}`;
    }
  }

  return `TIMEOUT: report not ready after ${maxAttempts} attempts`;
}

(async () => {
  for (const call of CALLS) {
    const tsv = await fetchReport(call.label, call.token, call.reportName);
    console.log(`\n========== FULL TSV OUTPUT — ${call.label} (${call.reportName}) ==========`);
    console.log(tsv);
    console.log(`========== END ${call.label} ==========\n`);
  }
})();
