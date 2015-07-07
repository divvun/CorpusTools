#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
#   This program compares goldstandard tmx files to files produced by the parallelizer pipeline 
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
#   along with program. If not, see <http://www.gnu.org/licenses/>.
#
#   Copyright 2011 Børre Gaup <borre.gaup@uit.no>
#

import os
import sys
import argparse
import lxml.etree

sys.path.append(os.environ['GTHOME'] + '/gt/script/langTools')
import parallelize

def parse_options():
    """
    Parse the command line. Expected input is one or more tmx goldstandard files.
    """
    parser = argparse.ArgumentParser(description = 'Compare goldstandard tmx files to files produced by the parallelizer pipeline.')
    
    args = parser.parse_args()
    return args

def main():
    args = parse_options()

    # Set the name of the file to write the test to
    paragstestfile = os.path.join(os.environ['GTHOME'], 'techdoc/ling/testruns.paragstesting.xml')
    
    # Initialize an instance of a tmx test data writer
    tester = parallelize.TmxGoldstandardTester(paragstestfile)
    tester.runTest()
    
if __name__ == '__main__':
    main()
    