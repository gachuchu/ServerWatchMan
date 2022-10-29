# @charset "utf-8"

# 設定ファイルの読み込み
. ".\LineConfig.ps1"

Start-Sleep -s 20

$endpoint="https://api.line.me/v2/bot/message/push"
$headers = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
$headers.Add("Content-Type", "application/json")
$headers.Add("Authorization", "Bearer {$($LineConfig.channel_access_token)}")

$payload = @{
	"to"=$LineConfig.to_user_id
	"messages"=@(
		@{
			"type"="text"
			"text"=$LineConfig.message
		}
	)
}
foreach($url in $LineConfig.imgurl) {
	$payload.messages += @{
		"type"="image"
		"originalContentUrl"=$url
		"previewImageUrl"=$url
	}
	if($payload.messages.Length -ge 5) {
		$body = $payload | ConvertTo-Json -Depth 4 -Compress
		$body = [System.Text.Encoding]::UTF8.GetBytes($body)
		Invoke-RestMethod $endpoint -Method 'POST' -Headers $headers -Body $body
		$payload.messages = @()
	}
}
if($payload.messages.Length -gt 0) {
	$body = $payload | ConvertTo-Json -Depth 4 -Compress
	$body = [System.Text.Encoding]::UTF8.GetBytes($body)
	Invoke-RestMethod $endpoint -Method 'POST' -Headers $headers -Body $body
}
