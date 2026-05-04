from . import (firecrawl, pexels, unsplash, pixabay, huggingface, whatthefont,
               yandex_wordstat, yandex_metrika, telegram, amocrm, bitrix24,
               beget_ssh, beget_api, cloudflare, regru)
from .base import ValidationResult

ALL = {
    "firecrawl": firecrawl.validate,
    "pexels": pexels.validate,
    "unsplash": unsplash.validate,
    "pixabay": pixabay.validate,
    "huggingface": huggingface.validate,
    "whatthefont": whatthefont.validate,
    "yandex_wordstat": yandex_wordstat.validate,
    "yandex_metrika": yandex_metrika.validate,
    "telegram": telegram.validate,
    "amocrm": amocrm.validate,
    "bitrix24": bitrix24.validate,
    "beget_ssh": beget_ssh.validate,
    "beget_api": beget_api.validate,
    "cloudflare": cloudflare.validate,
    "regru": regru.validate,
}


_MODULES = {
    "firecrawl": firecrawl,
    "pexels": pexels,
    "unsplash": unsplash,
    "pixabay": pixabay,
    "huggingface": huggingface,
    "whatthefont": whatthefont,
    "yandex_wordstat": yandex_wordstat,
    "yandex_metrika": yandex_metrika,
    "telegram": telegram,
    "amocrm": amocrm,
    "bitrix24": bitrix24,
    "beget_ssh": beget_ssh,
    "beget_api": beget_api,
    "cloudflare": cloudflare,
    "regru": regru,
}


def run_all(only: list[str] | None = None) -> list[ValidationResult]:
    services = only if only else list(ALL.keys())
    return [_MODULES[s].validate() for s in services if s in ALL]


def main() -> int:
    results = run_all()
    failed = 0
    for r in results:
        print(r)
        if not r.is_valid:
            failed += 1
    print(f"\n{len(results) - failed}/{len(results)} OK")
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
