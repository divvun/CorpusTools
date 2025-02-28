ORTHOGRAPHIES = {
    "sme": [
        "leem",
        "friis",
        "nielsen",
        "itkonen",
        "bergsland",
    ],
}


def orthographies(want_only_lang=None):
    for lang, orthgraphies in ORTHOGRAPHIES.items():
        if want_only_lang is not None and want_only_lang != lang:
            continue

        yield from orthgraphies


def is_orthography_of(ortho, lang):
    try:
        return ortho in ORTHOGRAPHIES[lang]
    except KeyError:
        return False
