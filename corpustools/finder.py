# -*- coding:utf-8 -*-

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
#   Copyright © 2016 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

from __future__ import print_function
from __future__ import unicode_literals

import collections
import difflib
import lxml.html
import os
import requests
import shutil
import sys
import urlparse

from corpustools import adder
from corpustools import move_files
from corpustools import namechanger
from corpustools import util
from corpustools import xslsetter


def main():
    #find_files_without_parallels()
    #find_not_analysed(sys.argv[1])
    #fix_pdf_filenames(sys.argv[1])
    move_twenty_percent_to_goldcorpus()


def print_equality_ratios_in_dir():
    ratios = set()
    for root, dirs, files in os.walk(sys.argv[1]):
        for f in files:
            if f.endswith('.html') and sys.argv[2] in f:
                path = os.path.join(root, f)
                sm = difflib.SequenceMatcher(a=path, b=path.replace(sys.argv[2], sys.argv[3]))
                ratios.add(round(sm.ratio(), 2))

    for ratio in ratios:
        print(ratio)

def remove_files_with_duplicate_content():
    '''To replace: 123, , 339, 340'''
    ufflangs = {
        u'fin': u'finnish',
        u'eng': u'english',
        u'sme': u'davvi',
        u'smn': u'anaras',
        u'sms': u'nuortta'
    }

    this_lang = u'sms'

    foundcount = 0
    notfoundcount = 0
    fingetter = adder.AddToCorpus(unicode(os.getenv('GTFREE')), u'fin', u'admin/sd/www.samediggi.fi')
    smsgetter = adder.AddToCorpus(unicode(os.getenv('GTFREE')), this_lang, u'admin/sd/www.samediggi.fi')
    for root, dirs, files in os.walk(os.path.join(os.getenv('GTFREE'), 'orig', this_lang,
                                                  u'admin/sd/www.samediggi.fi')):
        print(root)
        for f in files:
            if f.endswith('.xsl') and 'itemid=256' in f:
                path = os.path.join(root, f)
                mdh = xslsetter.MetadataHandler(path)
                filename = mdh.get_variable('filename')

                parallellfile = path.replace('/' + this_lang + '/', '/fin/')
                parallellfile = parallellfile.replace('.xsl', '')
                parallellfile = parallellfile.replace('lang=' + ufflangs[this_lang], 'lang=finnish')
                parallellfile = parallellfile.replace('itemid=256', 'itemid=195')

                if not os.path.exists(parallellfile):
                    if this_lang != 'fin':
                        fingetter.copy_url_to_corpus(filename.replace('Itemid=256', 'Itemid=195').replace('lang=' + ufflangs[this_lang], 'lang=finnish'))

                smsgetter.copy_url_to_corpus(filename.replace('Itemid=256', 'Itemid=195'),
                                             parallelpath=parallellfile)
                move_files.mover(path.replace('.xsl', ''), '')

    smsgetter.add_files_to_working_copy()
    fingetter.add_files_to_working_copy()


def adder_adderexception_invalid_url():
    langs = ['davvi', 'finnish', 'nuortta', 'anaras', 'english']
    downloader = adder.UrlDownloader(os.path.join(os.getenv('GTFREE'), 'klaff'))
    for lang in langs:
        try:
            (r, tmpname) = downloader.download('http://www.samediggi.fi/index2.php?option=com_content&task=view&id=420&pop=1&page=0&Itemid=149', params={'lang': lang})
        except adder.AdderException as e:
            print('her gikk det galt', str(e))


def print_finder():
    langs = {
        'eng': 'english',
        'fin': 'finnish',
        'sme': 'davvi',
        'smn': 'anaras',
        'sms': 'nuortta',
    }

    file_count = 0
    img_count = 0

    downloader = adder.UrlDownloader(
        os.path.join(os.getenv('GTFREE'), 'tmp'))

    for lang in langs.keys():
        for root, dirs, files in os.walk(os.path.join(os.getenv('GTFREE'), 'orig', lang, 'admin/sd/www.samediggi.fi')):
            for f in files:
                if f.endswith('.html'):
                    file_count += 1
                    path = os.path.join(root, f)
                    tree = lxml.html.parse(path)
                    print_img = tree.find('.//img[@src="http://www.samediggi.fi/images/M_images/printButton.png"]')
                    if print_img is not None:
                        img_count += 1
                        parent = print_img.getparent()
                        href = urlparse.urlparse(parent.get('href'))

                        query = href.query
                        newquery = [part for part in query.split('&')
                                    if (part.startswith('option') or
                                        part.startswith('id') or
                                        part.startswith('task'))]
                        newquery.append('lang=' + langs[lang])

                        newhref = urlparse.urlunparse(
                            (href.scheme,
                             href.netloc,
                             href.path,
                             href.params,
                             '&'.join(newquery),
                             href.fragment))

                        print('about to download', newhref)
                        (r, tmpname) = downloader.download(newhref)

                        newname = namechanger.normalise_filename(os.path.basename(newhref)) + '.html'

                        newpath = os.path.join(root, newname)
                        with open(newpath, 'w') as newfile:
                            newfile.write(r.content)
                        print('written', newpath)
                        print()

                    else:
                        print('!!!!!!')


def remove_if_no_smX():
    langs = {
        'eng': 'english',
        'fin': 'finnish',
        'sme': 'davvi',
        'smn': 'anaras',
        'sms': 'nuortta',
    }

    file_count = 0
    img_count = 0

    downloader = adder.UrlDownloader(
        os.path.join(os.getenv('GTFREE'), 'tmp'))

    for lang1 in ['eng', 'fin']:
        for root, dirs, files in os.walk(
            os.path.join(os.getenv('GTFREE'),
                         'orig', lang1, 'admin/sd/www.samediggi.fi')):
            for f in files:
                if f.endswith('.html'):
                    file_count += 1
                    path = os.path.join(root, f)

                    smx_exists = False
                    for lang2 in ['sme', 'smn', 'sms']:
                        smxpath = path.replace(
                            'orig/' + lang1,
                            'orig/' + lang2)
                        smxpath = smxpath.replace(
                            '_lang=' + langs[lang1],
                            '_lang=' + langs[lang2])
                        if os.path.exists(smxpath):
                            smx_exists = True

                    if smx_exists is False:
                        move_files.mover(path, '')

def find_files_without_parallels():
    url_to_filename = {}
    for root, dirs, files in os.walk(sys.argv[1]):
        for f in files:
            if f.endswith('.xsl'):
                file_ = os.path.join(root, f)
                mdh = xslsetter.MetadataHandler(file_)
                url_to_filename[mdh.get_variable('filename')] = file_

    urlset = set(url_to_filename.keys())

    newcounter = 0
    oldcounter = 0
    print_part = 'layout/set/print'
    downloader = adder.UrlDownloader(os.path.join(os.getenv('GTFREE'), 'tmp'))
    for url in urlset:
        if print_part not in url and '.aspx' not in url:
            parts = urlparse.urlsplit(url)
            nurl = urlparse.urlunparse((
                parts.scheme,
                os.path.join(parts.netloc, print_part),
                parts.path,
                '',
                parts.query,
                parts.fragment
            ))
            util.print_frame(debug=nurl)
            try:
                (r, tmpname) = downloader.download(nurl)
                newfilename = namechanger.normalise_filename(os.path.basename(tmpname))
                newpath = os.path.join(os.path.dirname(url_to_filename[url]), newfilename)
                oldpath = url_to_filename[url].replace('.xsl', '')

                if os.path.exists(newpath) and oldpath != newpath:
                    shutil.copy(tmpname, newpath)
                    move_files.mover(oldpath, '')
                    mdh = xslsetter.MetadataHandler(newpath + '.xsl')
                    mdh.set_variable('filename', nurl)
                    mdh.write_file()
                elif oldpath != newpath:
                    mdh = xslsetter.MetadataHandler(oldpath + '.xsl')
                    mdh.set_variable('filename', nurl)
                    mdh.write_file()
                    move_files.mover(oldpath, newpath)
                else:
                    mdh = xslsetter.MetadataHandler(oldpath + '.xsl')
                    mdh.set_variable('filename', nurl)
                    mdh.write_file()
                    shutil.copy(tmpname, oldpath)

            except adder.AdderException as e:
                util.print_frame(debug=str(e))

    print('new files', newcounter)
    print('old files', oldcounter)


def find_not_analysed(directory):
    for root, dirs, files in os.walk(directory):
        for f in files:
            ana_root = root.replace('converted/', 'analysed/')
            ana_file = os.path.join(ana_root, f)
            orig_root = root.replace('converted/', 'orig/')
            orig_file = os.path.join(orig_root, f.replace('.xml', ''))
            if 'plenum_no/dc' not in ana_file and not os.path.exists(ana_file) and os.path.exists(orig_file):
                print(os.path.join(root, f))


def find_no_sami_parallel(directory):
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith('.xsl'):
                file_ = os.path.join(root, f)
                mdh = xslsetter.MetadataHandler(file_)
                p = mdh.get_parallel_texts()

                for lang in p.keys():
                    if lang in ['sme', 'sma', 'smj', 'smn', 'sms']:
                        break
                else:
                    move_files.mover(file_[:-4], '')


def fix_pdf_filenames(directory):
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith('.pdf'):
                file_ = os.path.join(root, f).decode('utf8')
                mdh = xslsetter.MetadataHandler(file_ + u'.xsl')
                url = mdh.get_variable('filename')
                #print(file_, url)

                downloader = adder.UrlDownloader(os.path.join(os.getenv('GTFREE'), 'tmp'))
                with util.ignored(KeyError):
                    try:
                        (r, tmpname) = downloader.download(url)
                    except adder.AdderException as e:
                        print(str(e))
                    else:
                        newfilename = namechanger.normalise_filename(os.path.basename(tmpname))
                        if newfilename != f:
                            util.print_frame(debug=newfilename)
                            move_files.mover(file_, os.path.join(root, newfilename))


def move_twenty_percent_to_goldcorpus():
    '''Move twenty percent of the files to the goldcorpus'''
    directories = ['orig/sme/admin/sd/cealkamusat_fi',
                   'orig/sme/admin/sd/davviriikkalas_samekonvensuvdna_fi',
                   'orig/sme/admin/sd/inaugurations_fi',
                   'orig/sme/admin/sd/ohcan_lahkai_fi',
                   'orig/sme/admin/sd/sami_parlamentarals_raddi_fi',
                   'orig/sme/admin/sd/www.samediggi.fi',
                   'orig/sme/facta/samediggi.fi/']

    fluff = collections.defaultdict(list)
    for dir in directories:
        for root, dirs, files in os.walk(os.path.join(os.getenv('GTFREE'), dir)):
            for f in files:
                if f.endswith('.xsl'):
                    name = os.path.join(root, f[:-4])
                    size = os.path.getsize(name)
                    fluff[size].append(name)

    i = 0
    for size in sorted(fluff.keys(), reverse=True):
        for f in fluff[size]:
            if i == 4:
                move_files.mover(f, f.replace('orig/', 'goldstandard/orig/'))
                i = 0
            i += 1
