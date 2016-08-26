#coding=utf-8
#
# Copyright (c) 2016, Intel Corporation.
# Author Simo Kuusela <simo.kuusela@intel.com>
# Author Igor Stoppa <igor.stoppa@intel.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms and conditions of the GNU General Public License,
# version 2, as published by the Free Software Foundation.
#
# This program is distributed in the hope it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#

"""Setup for gadget keyboard emulator"""

from setuptools import setup

PROJECT_NAME = "gadget_kb_emulator"
setup(
    name = "gadget_kb_emulator",
    description="Gadget keyboard emulator",
    version = "0.1",
    author = "Simo Kuusela, Igor Stoppa",
    author_email = "simo.kuusela@intel.com, igor.stoppa@intel.com",
    package_dir={PROJECT_NAME: "src"},
    packages=[PROJECT_NAME],
    include_package_data=True
)
