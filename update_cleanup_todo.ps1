$json = Get-Content .cleanup-todo.json | ConvertFrom-Json
$newList = @()

# Remove indices 30-39
for ($i = 0; $i -lt $json.Count; $i++) {
  if ($i -lt 30 -or $i -ge 40) {
    $newList += $json[$i]
  }
}

$newList | ConvertTo-Json -Compress | Set-Content .cleanup-todo.json
Write-Host "Updated .cleanup-todo.json: removed entries 30-39"
Write-Host "Remaining entries: $($newList.Count)"
