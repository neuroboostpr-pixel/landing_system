#!/usr/bin/env bats
load 'helpers.bash'

@test "compute_cache_key: одинаковые параметры → одинаковый ключ" {
    run python3 -c "
import sys, importlib.util
spec = importlib.util.spec_from_file_location('pp', '$PR_I_A_REPO_ROOT/skills/photo-curation/scripts/photo-pipeline.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Создать временный файл
from pathlib import Path
import tempfile
with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
    f.write(b'fake_jpg_content')
    p = Path(f.name)

k1 = mod.compute_cache_key(p, '#1a1a1a', 'auto', 'Dubai', '16:9')
k2 = mod.compute_cache_key(p, '#1a1a1a', 'auto', 'Dubai', '16:9')
k3 = mod.compute_cache_key(p, '#ff0000', 'auto', 'Dubai', '16:9')
assert k1 == k2, 'same inputs should give same key'
assert k1 != k3, 'different brand color should give different key'
print('OK')
"
    [ "$status" -eq 0 ]
    [[ "$output" == *"OK"* ]]
}
