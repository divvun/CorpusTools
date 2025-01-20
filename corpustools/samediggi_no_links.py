import re
from typing import Iterator
from urllib.parse import ParseResult, urlunparse

from lxml import etree

ADDRESS_RE = re.compile(r"((http(s)):\/\/)sametinget.no")
PATH_RE = re.compile(r"/\w")
PAGE_RE = re.compile(r"Side=\d(\d)?")
unwanted_endings = (
    ".pdf",
    ".jpg",
    ".docx",
    ".xlsx",
    ".csv",
    ".pptx",
    ".eps",
    ".doc",
    ".png",
    ".xls",
)


def get_filtered_links(
    parsed_url: ParseResult, html_element: etree._Element
) -> Iterator[str]:
    raw_adresses: Iterator[str | None] = (
        address_element.get("href")
        for address_element in html_element.xpath(".//a[@href]")
        if isinstance(address_element, etree._Element)
    )

    without_query_parameters = (
        (
            remove_page_reference(address, parsed_url=parsed_url)
            if PATH_RE.match(address)
            else address.split("?")[0]
        )
        for address in raw_adresses
        if address is not None
    )

    return (
        address
        for address in without_query_parameters
        if is_valid_address(address.lower())
    )


def remove_page_reference(path: str, parsed_url: ParseResult) -> str:
    match = PAGE_RE.search(path)
    return urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            path.split("?")[0],
            "",
            f"{match.group(0)}" if match else "",
            "",
        )
    )


def is_valid_address(href: str) -> bool | None:
    """Check if this is an address that should be crawled."""
    match = ADDRESS_RE.match(href)
    return (
        match
        and not re.search(
            "sametingets-vedtak-1989-2004|endresprak.aspx|innsyn.aspx|/english/|/#|"
            "sametingets-representanter|samedikki-airasat|samedikke-ajrrasa|saemiedigkien-tjirkijh|"
            "plenumssaker|dievascoahkkinassit|allestjahkanimassje|stoerretjaanghkoeaamhtesh|"
            "ofte-stilte-sporsmal|davja-jerron-gazaldagat",
            href,
        )
        and not href.endswith(unwanted_endings)
    )
