const xlsx = require('xlsx');
const fs = require('fs');

function parseFile(filename) {
  const wb = xlsx.readFile(filename);
  const ws = wb.Sheets[wb.SheetNames[0]];
  const data = xlsx.utils.sheet_to_json(ws, { header: 1 });
  
  console.log(`\n=== ${filename} ===`);
  console.log(`Rows: ${data.length}`);
  console.log(`Headers: ${data[0]?.join(' | ')}`);
  console.log(`\nFirst 3 data rows:`);
  data.slice(1, 4).forEach((row, i) => {
    console.log(`Row ${i+1}: ${row.slice(0, 8).join(' | ')}`);
  });
  
  // Find key columns
  const headers = data[0] || [];
  const colMap = {};
  headers.forEach((h, i) => {
    if (h) colMap[h.toString().trim()] = i;
  });
  
  console.log(`\nColumn map:`, Object.keys(colMap).slice(0, 10));
  
  return { headers, data: data.slice(1), colMap };
}

const may = parseFile('project_225433_report-17_2026-05-01-2026-05-31.xlsx');
const june = parseFile('project_225433_report-17_2026-06-01-2026-06-15.xlsx');

// Save column maps for inspection
fs.writeFileSync('roistat_columns.json', JSON.stringify({
  may: { headers: may.headers, colMap: may.colMap },
  june: { headers: june.headers, colMap: june.colMap }
}, null, 2));
console.log('\nSaved column maps to roistat_columns.json');
