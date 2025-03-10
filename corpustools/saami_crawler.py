#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this file. If not, see <http://www.gnu.org/licenses/>.
#
#   Copyright © 2013-2023 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""This file contains routines to crawl sites containing saami text."""


import argparse

from corpustools import (
    argparse_version,
    # nrk_no_crawler,
    # samas_crawler,
    samediggi_fi_crawler,
    samediggi_no_crawler,
)
from corpustools.nrk_no_crawler import NrkNoCrawler


def parse_options():
    """Parse the commandline options.

    Returns:
        (argparse.Namespace): the parsed commandline arguments
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description="Crawl saami sites (for now, only samediggi.no and www.samediggi.fi).",
    )

    parser.add_argument("sites", nargs="+", help="The sites to crawl")

    args = parser.parse_args()
    return args


def main():
    """Crawl sites."""
    args = parse_options()

    crawlers = {
        "www.samediggi.fi": samediggi_fi_crawler.SamediggiFiCrawler(),
        "samediggi.no": samediggi_no_crawler.SamediggiNoCrawler(),
        "nrk.no": NrkNoCrawler(),
        # "samas.no": samas_crawler.SamasCrawler(),
    }

    for site in args.sites:
        crawler = crawlers[site]
        crawler.crawl_site()
