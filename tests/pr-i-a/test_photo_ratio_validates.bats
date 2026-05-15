#!/usr/bin/env bats
load 'helpers.bash'

@test "photo-pipeline crop_center: 16:9 фото в 9:16 слот → height сохраняется" {
    run python3 -c "
from pathlib import Path
import sys
sys.path.insert(0, '$PR_I_A_REPO_ROOT/skills/photo-curation/scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('photo_pipeline', '$PR_I_A_REPO_ROOT/skills/photo-curation/scripts/photo-pipeline.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

from PIL import Image
# 16:9 image
img = Image.new('RGB', (1920, 1080), (100, 100, 100))
# crop to 9:16 ratio
target_ratio = 9 / 16
cropped = mod.crop_center(img, target_ratio)
print(f'{cropped.width}x{cropped.height}')
assert abs(cropped.width / cropped.height - target_ratio) < 0.01
"
    [ "$status" -eq 0 ]
}
