# --
# Copyright (c) 2014-2025 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from __future__ import absolute_import

from pony import orm

db = orm.Database()
Entity = db.Entity


def Column(type_, nullable=False, **kw):
    return (orm.Required if nullable else orm.Optional)(type_, **kw)
