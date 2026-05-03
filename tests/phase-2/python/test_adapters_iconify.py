import responses
from tools.adapters.iconify import search


def test_search_parses_results(http_mock):
    http_mock.add(
        responses.GET,
        "https://api.iconify.design/search",
        json={
            "icons": ["lucide:arrow-right", "phosphor:arrow-right", "tabler:arrow-right"],
            "total": 3
        },
        status=200,
    )
    results = search("arrow-right", limit=10)
    assert len(results) == 3
    assert results[0] == {"prefix": "lucide", "name": "arrow-right", "id": "lucide:arrow-right"}


def test_search_with_prefix_filter(http_mock):
    http_mock.add(
        responses.GET,
        "https://api.iconify.design/search",
        json={"icons": ["lucide:check"], "total": 1},
        status=200,
    )
    results = search("check", prefix="lucide")
    assert results == [{"prefix": "lucide", "name": "check", "id": "lucide:check"}]
