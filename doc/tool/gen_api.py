#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


import sys, os
import pydoc

uarm_dir_name = os.path.dirname(__file__)
sys.path.append(os.path.join(uarm_dir_name, '../..'))

from uarm import SwiftAPI, SwiftAPIWrapper
from uarm import uarm_create, uarm_scan, uarm_scan_and_connect

from doc.tool.markdown_doc import MarkdownDoc

print('Writing SwiftAPIWrapper docs')
extended_docs_filename = os.path.join(
    uarm_dir_name, os.path.abspath('doc/api/swift_api_wrapper.md'))
if os.path.exists(extended_docs_filename):
    os.remove(extended_docs_filename)
open(extended_docs_filename, 'w', encoding='utf-8').write(
    pydoc.render_doc(uarm_create, renderer=MarkdownDoc()))
open(extended_docs_filename, 'a+', encoding='utf-8').write(
    pydoc.render_doc(uarm_scan, renderer=MarkdownDoc()))
open(extended_docs_filename, 'a+', encoding='utf-8').write(
    pydoc.render_doc(uarm_scan_and_connect, renderer=MarkdownDoc()))
open(extended_docs_filename, 'a+', encoding='utf-8').write(
    pydoc.render_doc(SwiftAPIWrapper, renderer=MarkdownDoc()))

print('Finished')

