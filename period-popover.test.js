const assert = require('node:assert/strict');
const fs = require('node:fs');

const html = fs.readFileSync(require('node:path').join(__dirname, 'index.html'), 'utf8');

assert.match(html, /id="periodTrigger"/);
assert.match(html, /id="periodPopover"/);
assert.match(html, /id="periodSearch"/);
assert.match(html, /class="pop-mode active"[^>]*aria-pressed="true"[^>]*data-mode="weeks"/);
assert.match(html, /class="pop-mode"[^>]*aria-pressed="false"[^>]*data-mode="months"/);
assert.match(html, /function renderPeriodList\(/);
assert.match(html, /function updatePeriodTrigger\(/);
assert.match(html, /function selectPeriodItem\(/);
assert.match(html, /function summarizeWeeks\(/);
assert.match(html, /return \[aggregateWeeks\(month\.weeks, month\.label, month\.id\)\]/);
assert.match(html, /data-preset="last4"/);
assert.match(html, /Escape/);

console.log('period popover structure: ok');
