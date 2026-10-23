from typing import Iterator

ORTHOGRAPHIES: dict[str, list[str]] = {
    "sme": [
        "leem",
        "friis",
        "nielsen",
        "itkonen",
        "bergsland",
    ],
}


def orthographies(want_only_lang: str | None=None) -> Iterator[str]:
    for lang, orthgraphies in ORTHOGRAPHIES.items():
        if want_only_lang is not None and want_only_lang != lang:
            continue

        yield from orthgraphies


def is_orthography_of(ortho: str, lang: str)-> bool:
    try:
        return ortho in ORTHOGRAPHIES[lang]
    except KeyError:
        return False
