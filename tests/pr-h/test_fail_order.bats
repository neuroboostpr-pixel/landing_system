#!/usr/bin/env bats
load 'helpers.bash'

@test "fail: порядок блоков отличается от prototype.yaml" {
    project="$(make_fake_project)"
    # Поменяем секции местами в composed.html
    python3 -c "
from pathlib import Path
p = Path('$project/07b_COMPOSED/composed.html')
text = p.read_text()
# swap: features section appears BEFORE hero section
hero = text.split('<section data-block=\"hero-1\">')[1].split('</section>')[0]
features = text.split('<section data-block=\"features-1\">')[1].split('</section>')[0]
new = text.replace(
    f'<section data-block=\"hero-1\">{hero}</section>',
    'HERO_PLACEHOLDER'
).replace(
    f'<section data-block=\"features-1\">{features}</section>',
    f'<section data-block=\"features-1\">{features}</section><section data-block=\"hero-1\">{hero}</section>'
).replace('HERO_PLACEHOLDER', '')
p.write_text(new)
"
    run bash "$PR_H_REPO_ROOT/scripts/verify-content-preserved.sh" "$project"
    [ "$status" -eq 1 ]
    [[ "$output" == *"Порядок блоков"* ]] || [[ "$output" == *"order"* ]]
}
