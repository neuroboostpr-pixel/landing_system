#!/usr/bin/env bats

REPO="$(cd "$(dirname "${BATS_TEST_FILENAME}")/../.." && pwd)"

@test "template/07c_PHOTOS exists with README" {
    [ -d "$REPO/template/07c_PHOTOS" ]
    [ -f "$REPO/template/07c_PHOTOS/README.md" ]
}

@test "template has all 7 inbox subfolders" {
    for sub in "_свалка" "портреты_и_команда" "процесс_работы" "объекты_и_продукты" "интерьер_экстерьер" "до_после" "документы_сертификаты"; do
        [ -d "$REPO/template/07c_PHOTOS/inbox/$sub" ] || {
            echo "Missing subfolder: $sub"
            return 1
        }
    done
}

@test "every named subfolder has a README" {
    for sub in "портреты_и_команда" "процесс_работы" "объекты_и_продукты" "интерьер_экстерьер" "до_после" "документы_сертификаты"; do
        [ -f "$REPO/template/07c_PHOTOS/inbox/$sub/README.md" ] || {
            echo "Missing README in $sub"
            return 1
        }
    done
}

@test "_свалка has .gitkeep" {
    [ -f "$REPO/template/07c_PHOTOS/inbox/_свалка/.gitkeep" ]
}

@test "main README mentions all 7 subfolders" {
    body="$(cat "$REPO/template/07c_PHOTOS/README.md")"
    for sub in "портреты_и_команда" "процесс_работы" "объекты_и_продукты" "интерьер_экстерьер" "до_после" "документы_сертификаты" "_свалка"; do
        echo "$body" | grep -q "$sub" || {
            echo "README doesn't mention $sub"
            return 1
        }
    done
}

@test "main README is in Russian and addresses marketer (not developer)" {
    body="$(cat "$REPO/template/07c_PHOTOS/README.md")"
    # Russian content markers
    echo "$body" | grep -qE "фотк|клиент|подпапк|слот"
    # /landing-photos command mentioned
    echo "$body" | grep -q "/landing-photos"
}
