from flask import Flask

from flask_registry import (BlueprintAutoDiscoveryRegistry,
                            ConfigurationRegistry, ExtensionRegistry,
                            PackageRegistry, Registry)


class Config(object):
    PACKAGES = ['registry_module']
    EXTENSIONS = ['registry_module.mockext']
    USER_CFG = True


def create_app(config):
    app = Flask('myapp')
    app.config.from_object(config)
    r = Registry(app=app)
    r['packages'] = PackageRegistry(app)
    r['extensions'] = ExtensionRegistry(app)
    r['config'] = ConfigurationRegistry(app)
    r['blueprints'] = BlueprintAutoDiscoveryRegistry(app=app)
    return app

if __name__ == '__main__':
    config = Config()
    app = create_app(config)
    app.run(debug=True)
