# Encoding: utf-8

# --
# Copyright (c) 2008-2021 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from os import path

from setuptools import setup, find_packages


here = path.normpath(path.dirname(__file__))

with open(path.join(here, 'README.rst')) as long_description:
    LONG_DESCRIPTION = long_description.read()

setup(
    name='nagare-services-database-pony',
    author='Net-ng',
    author_email='alain.poirier@net-ng.com',
    description='Nagare Pony ORM service',
    long_description=LONG_DESCRIPTION,
    license='BSD',
    keywords='',
    url='https://github.com/nagareproject/services-database-pony',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
    install_requires=['pony', 'nagare-services-transaction', 'nagare-server'],
    entry_points='''
        [nagare.commands]
        pony = nagare.admin.pony:Commands

        [nagare.commands.pony]
        create = nagare.admin.pony:Create
        drop = nagare.admin.pony:Drop

        [nagare.services]
        pony = nagare.services.pony:Pony
    '''
)
