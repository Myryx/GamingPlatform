
SETTINGS = {
    'config': {
        'sync_strategy': 'hot',  # 'hot' or 'cold'
        # hot - sync all the changes made to bot configuration
        #   (including l10n) during runtime with kv-storage so
        #   that they are available after bot restarted.
    },
    'bot': {
        'token':'196258875:AAGEVY52-hOHtlNXM_dCugtxtidONZp-cSU',
        'initial_state': 'StartLanguages',
        'initial_inline_state': '',
        'suppress_exceptions': True
    },
    'db_storage': {
        # Database storage is used to keep user sessions and other stuff.
        'type': 'inmemory',  # 'disk', 'mongo'
        'params': {
            # for type = 'mongo'
            'host': 'localhost',
            'port': 27017,
            'database': 'botlab_test',
            # for type = 'disk'
            'file_path': 'storage.json'
            # for type = 'inmemory'
            # - empty
        }
    },
    'kv_storage': {
        'type': 'inmemory',  # 'inmemory', 'redis'
        'params': {
            # for type = 'mongo', 'redis'
            'host': 'localhost',
            'port': 27017,
            'db': 'botlab_test',
            # for type = 'mongo' - collection with kv-pairs
            'collection': 'configs'
            # 'redis' is buggy, probably, because of python driver implementation,
            #   so, take care.

            # for type = 'inmemory'
            # - empty
        }
    },
    'l10n': {
        'default_lang': 'en',
        'file_path': 'l10n.json'
    },

}

