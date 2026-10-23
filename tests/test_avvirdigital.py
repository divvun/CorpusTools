from corpustools.avvirdigital import AvvirAuthor, convert_author


def test_extract_author():
    author_dict = {  # type: ignore
        "content": {
            "link": [{"insert": "kila@avvir.no"}],
            "name": [{"insert": "Kila Johanne Anti"}],
        },
        "id": "doc-1ha25rpi60",
        "identifier": "author",
        "styles": {},
    }

    assert convert_author(author_dict["content"]["name"][0]["insert"]) == AvvirAuthor(  # type: ignore
        forname="Kila Johanne",
        surname="Anti",
    )
