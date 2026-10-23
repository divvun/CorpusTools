import pytest

from corpustools.avvirdigital import AvvirAuthor, convert_author


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
