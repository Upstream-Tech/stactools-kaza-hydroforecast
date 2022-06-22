import stactools.core
from stactools.cli.registry import Registry

from stactools.kaza_hydroforecast.stac import create_collection, create_item

__all__ = ["create_collection", "create_item"]

stactools.core.use_fsspec()


def register_plugin(registry: Registry) -> None:
    from stactools.kaza_hydroforecast import commands

    registry.register_subcommand(commands.create_kazahydroforecast_command)


__version__ = "1.0.0"
