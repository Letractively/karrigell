class ConfigError(Exception):
    pass

def check(apps):
    for app in apps:
        if not app.root_url.startswith('/'):
            raise ConfigError('Root url {} does not start with "/"'.format(app.root_url))