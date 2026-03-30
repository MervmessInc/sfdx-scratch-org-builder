from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("sf-org-manager")
except PackageNotFoundError:
    __version__ = "0.1.0.dev"


