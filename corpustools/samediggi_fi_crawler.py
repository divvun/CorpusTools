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


import os
import re
from urllib.parse import urlparse, urlunparse

import requests
from lxml import html, etree

from corpustools import adder, crawler, util, xslsetter


class SamediggiFiCrawler(crawler.Crawler):
    """Notes about samediggi.fi.

    Start page is:
    http://www.samediggi.fi/index.php?option=com_frontpage&Itemid=39


    Empty pages contain either
    * "Käännöstä ei ole saatavilla"
    * "There are no translations available"

    Follow links starting with:
    * http://www.samediggi.fi/index (www.samediggi.fi == samediggi.fi)
    * index: prepend these adresses with http://www.samediggi.fi

    Remove any &lang=* parts from links,
    then re-add languages
    * &lang=finnish
    * &lang=davvi
    * &lang=anaras
    * &lang=nuortta
    * &lang=english

    Main content in div id="keski_mainbody"
    Content parts in table class="contentpaneopen"

    www.samediggi.fi/nuorat is a separate "domain"
    Links start with:
    * http://www.samediggi.fi/nuorat
    * nuorat/index

    languages
    * &lang=fi
    * &lang=dav
    * &lang=an
    * &lang=nuo
    * &lang=en

    Same procedure with links here
    """

    def __init__(self):
        """Initialise the SamediggiFiCrawler class."""
        super().__init__()

        self.unvisited_links.add("http://www.samediggi.fi/")
        self.old_urls = {}
        self.langs = {
            "fi": "fin",
            "dav": "sme",
            "an": "smn",
            "nuo": "sms",
            "en": "eng",
        }

        self.content_types = [
            "text/html",
            "application/msword",
            "application/pdf",
            "text/plain",
        ]

        for natural, iso in self.langs.items():
            self.corpus_adders[natural] = adder.AddToCorpus(
                self.goaldir / f"corpus-{iso}-orig", "admin/sd/www.samediggi.fi"
            )

        # self.get_old_urls()

    def get_old_urls(self):
        """Collect the urls of already downloaded pages."""
        for _, corpus_adder in self.corpus_adders.items():
            for root, _, files in os.walk(corpus_adder.corpusdir):
                for file_ in files:
                    if file_.endswith(".xsl"):
                        path = os.path.join(root, file_)
                        mdh = xslsetter.MetadataHandler(path)
                        self.old_urls[mdh.get_variable("filename")] = path.replace(
                            ".xsl", ""
                        )

    def crawl_site(self):
        """Crawl samediggi.fi."""
        while self.unvisited_links:
            link = self.unvisited_links.pop()
            if link not in self.visited_links:
                util.print_frame(debug=link.encode("utf8"))
                util.print_frame(
                    debug=f"Before: unvisited_links {len(self.unvisited_links)}"
                )

                parallel_pages = []
                found_saami = False
                for lang in self.langs.keys():
                    result = requests.get(link, params={"lang": lang})

                    print(result.headers["content-type"])

                    if not any(
                        contType in result.headers["content-type"]
                        for contType in self.content_types
                    ):
                        break

                    if result.history:
                        print("history", result.history)

                    if "samediggi.fi" not in result.url:
                        print("url", result.url)

                    if (
                        "www.samediggi.fi" in result.url
                        and result.status_code == requests.codes.ok
                        and not self.invalid_content(str(result.content, "utf-8"))
                    ):
                        if lang in ["dav", "an", "nuo"]:
                            found_saami = True
                        self.harvest_links(result.content)

                        parallel_pages.append((result.url, lang))
                        # print_url = self.get_print_url(result.content, lang)
                        # if print_url is not None:
                        #     parallel_pages.append((print_url, lang))
                    else:
                        if "samediggi.fi" not in result.url:
                            util.print_frame(
                                debug="Not fetching {} which was {}\n".format(
                                    result.url.encode("utf8"), link.encode("utf8")
                                )
                            )

                if found_saami and parallel_pages:
                    self.save_pages(parallel_pages)
                    for page in parallel_pages:
                        self.visited_links.add(
                            self.remove_lang_from_url(page[0]).strip()
                        )

                util.print_frame(
                    debug=f"After: unvisited_links {len(self.unvisited_links)}"
                )

            self.visited_links.add(link)
            util.print_frame(debug=f"visited_links {len(self.visited_links)}\n")
            # break  # only front page

    @staticmethod
    def get_print_url(content, lang):
        """Compute the print url of the page."""
        tree = html.document_fromstring(content)
        print_img = tree.find(
            './/img[@src="http://www.samediggi.fi/' 'images/M_images/printButton.png"]'
        )

        if print_img is not None:
            parent = print_img.getparent()
            href = urlparse(parent.get("href"))

            query = href.query
            newquery = [
                part
                for part in query.split("&")
                if (
                    part.startswith("option")
                    or part.startswith("id")
                    or part.startswith("task")
                )
            ]
            newquery.append("lang=" + lang)

            newhref = urlunparse(
                (
                    href.scheme,
                    href.netloc,
                    href.path,
                    href.params,
                    "&".join(newquery),
                    href.fragment,
                )
            )

            return newhref

    @staticmethod
    def invalid_content(content):
        """Return true if the page does not contain the strings.

        * "Käännöstä ei ole saatavilla"
        * "There are no translations available"
        """
        return (
            "ei ole saatavilla" in content
            or "There are no translations available" in content
            or '<div class="login-form">' in content
            or "Sinulla ei ole tarvittavia" in content
            or "You need to login" in content
        )

    def harvest_links(self, content):
        """Harvest all links, bar some restrictions.

        Insert links into a set

        Discard links containing a href=
        * "#"
        * "*do_pdf*"
        * "pop=1"
        * com_events
        * com_search
        * www.samediggi.fi/haettavana
        * http://klemetti.blogspot.com/

        Don't follow (don't save content), but save links containg
        doc_download
        """
        try:
            tree = html.document_fromstring(content)
        except etree.ParserError:
            return

        for address in tree.findall(".//a"):
            href = address.get("href")
            if href is not None:
                href = self.remove_lang_from_url(href).strip()

                if not href.startswith("http"):
                    href = os.path.join("http://www.samediggi.fi", href)

                if (
                    href not in self.visited_links
                    and not re.search(
                        "klemetti.blogspot|/nuorat|/#|com_events|"
                        "com_search|haettavana|do_pdf|pop=1|com_docman|"
                        "/images|com_weblink|task=vcard|view_contact_id|"
                        "com_contact|mad4joomla|mailto|javascript|"
                        "administrator/",
                        href,
                    )
                    and (
                        href.startswith("http://www.samediggi.fi")
                        or href.startswith("https://www.samediggi.fi")
                    )
                ):
                    self.unvisited_links.add(href)

    def remove_lang_from_url(self, url):
        """Removes language specifier from end of urls"""
        url = url.replace("?lang=fi", "")
        url = url.replace("?lang=dav", "")
        url = url.replace("?lang=an", "")
        url = url.replace("?lang=nuo", "")
        url = url.replace("?lang=en", "")
        url = url.replace("&lang=fi", "")
        url = url.replace("&lang=dav", "")
        url = url.replace("&lang=an", "")
        url = url.replace("&lang=nuo", "")
        url = url.replace("&lang=en", "")
        return url
