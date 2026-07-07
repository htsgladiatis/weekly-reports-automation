$content = Get-Content "bitrix.py" -Raw
$old = 'WEBHOOK_URL = os.environ.get("BITRIX_WEBHOOK_URL", "")'
$new = '# WEBHOOK_URL = os.environ.get("BITRIX_WEBHOOK_URL", "")
WEBHOOK_URL = "https://dunegroup.bitrix24.ru/rest/396/vk0fdm6r1qrtt81w/"'
$content = $content -replace [regex]::Escape($old), $new
Set-Content -Path "bitrix.py" -Value $content
Write-Host "Updated!"