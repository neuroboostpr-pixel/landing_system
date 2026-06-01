$blocks = @(
  'features-minimal-grid-2-sskrusgun-ru-10',
  'features-minimal-grid-2-sskrusgun-ru-4',
  'features-minimal-grid-2-zilant-group-6',
  'features-minimal-grid-4-zilant-group-2',
  'features-playful-cards-opt-ecowash-ru-2',
  'features-playful-centered-medregistrant-ru-2',
  'features-technical-centered-medregistrant-ru-4',
  'features-technical-centered-portfolio-kdm1-ru-5',
  'features-technical-grid-2-portfolio-kdm1-ru-8',
  'features-technical-grid-2-romanmelnikov-tilda-3'
)

$deleted = 0
foreach ($block in $blocks) {
  $path = "block-library/features/$block"
  if (Test-Path $path) {
    Remove-Item -Recurse -Force $path
    Write-Host "DELETE: $block"
    $deleted++
  } else {
    Write-Host "SKIP: $block (not found)"
  }
}

Write-Host ""
Write-Host "Deleted $deleted/$($blocks.Count) blocks"
