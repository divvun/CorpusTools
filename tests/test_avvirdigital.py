import pytest

from corpustools.avvirdigital import (
    AvvirAuthor,
    AvvirTaggedText,
    convert_author,
    convert_image,
    convert_slideshow,
    convert_tagged_text,
)


@pytest.mark.parametrize(
    ("author_dict", "expected"),
    [
        (
            {
                "content": {
                    "link": [{"insert": "kila@avvir.no"}],
                    "name": [{"insert": "Kila Johanne Anti"}],
                },
                "id": "doc-1ha25rpi60",
                "identifier": "author",
                "styles": {},
            },
            AvvirAuthor(
                forname="Kila Johanne",
                surname="Anti",
            ),
        ),
        (
            {
                "content": {},
                "id": "doc-1gbpahpoh0",
                "identifier": "author",
                "styles": {},
            },
            None,
        ),
    ],
)
def test_extract_author(author_dict: dict[str, object], expected: AvvirAuthor) -> None:

    assert convert_author(author_dict) == expected


@pytest.mark.parametrize(
    ("faktatittel_dict", "expected"),
    [
        (
            {
                "content": {"text": [{"insert": "– Eat báljo"}]},
                "id": "doc-1g7jtcaf70",
                "identifier": "faktatittel",
                "styles": {},
            },
            AvvirTaggedText(text="– Eat báljo", tag="faktatittel"),
        ),
        (
            {
                "content": {"text": [{"insert": "– Eat báljo"}]},
                "id": "doc-1g7jtcaf70",
                "identifier": "faktatekst",
                "styles": {},
            },
            AvvirTaggedText(text="– Eat báljo", tag="faktatekst"),
        ),
        (
            {  # type: ignore
                "content": {"text": [{"insert": "– Eat báljo"}]},
                "id": "doc-1g7jtcaf70",
                "identifier": "body",
                "styles": {},
            },
            AvvirTaggedText(text="– Eat báljo", tag="body"),
        ),
    ],
)
def test_extract_faktatittel(
    faktatittel_dict: dict[str, object], expected: AvvirTaggedText
) -> None:
    assert convert_tagged_text(faktatittel_dict) == expected  # type: ignore


def test_extract_image() -> None:
    image_dict = {  # type: ignore
        "content": {"caption": [{"insert": "– Eat báljo"}]},
        "id": "doc-1g7jtcaf70",
        "identifier": "image",
        "styles": {},
    }
    assert convert_image(image_dict) == AvvirTaggedText(text="– Eat báljo", tag="image")  # type: ignore


@pytest.mark.parametrize(
    ("slideshow_dict", "expected"),
    [
        (
            {
                "containers": {
                    "slideshow": [
                        {
                            "content": {
                                "caption": [{"insert": "600 BEAIVVI MAŊŊEL:"}],
                                "image": {"id": "7F-MPMgW4yZB1eJpbjde0a"},
                            },
                            "id": "doc-1h21eqkqp0",
                            "identifier": "image",
                            "styles": {"fitting": "_fit-frame-height-to-content"},
                        },
                        {
                            "content": {
                                "caption": [{"insert": "Lávvordaga ledje"}],
                                "image": {"id": "3R9AprSyKPVA5TjwSI4m8a"},
                            },
                            "id": "doc-1h21eqnkt0",
                            "identifier": "image",
                            "styles": {"fitting": "_fit-frame-height-to-content"},
                        },
                    ]
                },
                "content": {},
                "id": "doc-1h21eqh530",
                "identifier": "slideshow",
                "styles": {},
            },
            AvvirTaggedText(
                text=("600 BEAIVVI MAŊŊEL: Lávvordaga ledje"), tag="slideshow"
            ),
        ),
        (
            {
                "containers": {
                    "slideshow": [
                        {
                            "content": {
                                "caption": [{"insert": "600 BEAIVVI MAŊŊEL:"}],
                                "image": {"id": "7F-MPMgW4yZB1eJpbjde0a"},
                            },
                            "id": "doc-1h21eqkqp0",
                            "identifier": "image",
                            "styles": {"fitting": "_fit-frame-height-to-content"},
                        },
                        {
                            "content": {
                                "caption": [{"insert": "600 BEAIVVI MAŊŊEL:"}],
                                "image": {"id": "3R9AprSyKPVA5TjwSI4m8a"},
                            },
                            "id": "doc-1h21eqnkt0",
                            "identifier": "image",
                            "styles": {"fitting": "_fit-frame-height-to-content"},
                        },
                    ]
                },
                "content": {},
                "id": "doc-1h21eqh530",
                "identifier": "slideshow",
                "styles": {},
            },
            AvvirTaggedText(text=("600 BEAIVVI MAŊŊEL:"), tag="slideshow"),
        ),
    ],  # type: ignore
)
def test_extract_slideshow(
    slideshow_dict: dict[str, object], expected: AvvirTaggedText
) -> None:
    assert convert_slideshow(slideshow_dict) == expected  # type: ignore
