# --
# Copyright (c) 2008-2023 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from nagare.admin import command


class Commands(command.Commands):
    DESC = 'Pony ORM subcommands'


class Command(command.Command):
    WITH_STARTED_SERVICES = True

    def _create_services(self, *args, **kw):
        return super(Command, self)._create_services(ignore_check_tables='on', *args, **kw)


class Create(Command):
    DESC = 'Create the database tables of an application'

    def set_arguments(self, parser):
        super(Create, self).set_arguments(parser)

        parser.add_argument('--drop', action='store_true', help='drop the database tables before to re-create them')

    @staticmethod
    def run(pony_service, application_service, drop=False):
        if drop:
            pony_service.drop_all()

        pony_service.create_all()
        pony_service.populate_all(application_service.service)


class Drop(Command):
    DESC = 'Drop the database tables of an application'

    @staticmethod
    def run(pony_service):
        pony_service.drop_all()
