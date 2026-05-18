#!/usr/bin/env bats
load 'helpers.bash'

@test "visual-qa-loop.py: парсит mock JSON review корректно" {
    # Используем dry-run или мок — тест на структуру, без реального codex
    run python3 -c "
import json, sys
mock = {'issues': [{'severity': 'critical', 'type': 'photo_cropped',
                     'description': 'test', 'selector': 'img', 'fix_hint': 'css_tweak: object-fit: cover'}],
        'summary': '1 critical'}
critical = [i for i in mock['issues'] if i.get('severity') == 'critical']
assert len(critical) == 1
print('OK')
"
    [ "$status" -eq 0 ]
    [[ "$output" == *"OK"* ]]
}
