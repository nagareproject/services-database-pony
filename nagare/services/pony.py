# --
# Copyright (c) 2008-2021 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

import logging

import transaction
from nagare.server import reference
from nagare.services import plugin
from nagare.services.transaction import TransactionHandler
from pony.orm import core, db_session


class PonyDataManager(object):

    tpc_vote = tpc_finish = tpc_abort = lambda *args: None

    @property
    def savepoint(self):
        raise NotImplementedError

    @staticmethod
    def tpc_begin(_):
        core.flush()

    @staticmethod
    def abort(_):
        core.rollback()
        db_session.__exit__()

    @staticmethod
    def commit(_):
        core.commit()
        db_session.__exit__()

    @staticmethod
    def sortKey():
        return "~ponydatamanager"

    @staticmethod
    def should_retry(error):
        retry_exceptions = db_session.retry_exceptions
        if not retry_exceptions:
            return False

        return retry_exceptions(error) if callable(retry_exceptions) else (error in retry_exceptions)


pony_data_manager = PonyDataManager()

# -----------------------------------------------------------------------------


def default_populate(app):
    pass


class Pony(plugin.Plugin):
    LOAD_PRIORITY = TransactionHandler.LOAD_PRIORITY + 1
    CONFIG_SPEC = dict(
        plugin.Plugin.CONFIG_SPEC,
        debug='boolean(default=False)',  # Set the database engine in debug mode?
        debug_with_values='boolean(default=False)',
        stats='boolean(default=False)',
        check_tables='boolean(default=True)',
        _ignore_check_tables='string(default=${ignore_check_tables:off})',
        __many__={  # Database sub-sections
            'activated': 'boolean(default=True)',
            'provider': 'option({})'.format(', '.join(core.known_providers)),
            'db': 'string(default="nagare.pony:db")',
            'populate': 'string(default="nagare.services.pony:default_populate")',
        }
    )

    def __init__(
            self,
            name, dist,
            debug=False, debug_with_values=False, stats=False,
            check_tables=True, _ignore_check_tables=False,
            **configs
    ):
        super(Pony, self).__init__(
            name, dist,
            debug=debug, debug_with_values=debug_with_values, stats=stats,
            check_tables=check_tables,
            **configs
        )

        self.debug = debug
        self.debug_with_values = debug_with_values
        self.stats = stats
        self.check_tables = check_tables and (_ignore_check_tables == 'off')
        self.configs = configs
        self.dbs = []

        core.set_sql_debug(debug, debug_with_values)

        core.orm_logger = self.logger
        core.sql_logger = logging.getLogger(self.logger.name + '.sql')

    @staticmethod
    def _bind(db, provider, activated, populate, **config):
        db = reference.load_object(db)[0]
        db.bind(provider=provider, create_db=True, **config)

        return db

    def handle_interactive(self):
        core.set_sql_debug(self.debug, self.debug_with_values)

        db_session.__enter__()
        transaction.get().join(pony_data_manager)

        return {}

    def handle_start(self, app):
        self.dbs = [self._bind(**config) for config in self.configs.values() if config['activated']]

        for db in self.dbs:
            db.generate_mapping(check_tables=self.check_tables)

    def handle_request(self, chain, **params):
        self.handle_interactive()

        r = chain.next(**params)

        if self.stats:
            for db in self.dbs:
                db.merge_local_stats()

        return r

    def drop_all(self):
        for db in self.dbs:
            db.drop_all_tables(True)

    def create_all(self):
        for db in self.dbs:
            db.create_tables()

    def populate_all(self, app):
        with db_session:
            populates = [reference.load_object(config['populate'])[0] for config in self.configs.values()]

            for populate in populates:
                populate(app)
