import os

class ConfigError(Exception):
    pass

def check(apps):
    for app in apps:
        # root_url start with /
        if not app.root_url.startswith('/'):
            raise ConfigError('Root url {} does not start with "/"'.format(app.root_url))
        # root dir exists
        if not os.path.exists(app.root_dir):
            raise ConfigError('Root directory {} does not exist'.format(app.root_dir))
        