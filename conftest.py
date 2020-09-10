import os
import pytest


def pytest_addoption(parser):
    parser.addoption(
        "-E",
        action="store",
        metavar="NAME",
        help="only run tests matching the environment NAME.",
    )

    parser.addoption(
        "--with-tox",
        default=False,
        action="store_true"
    )
    
    return


def pytest_configure(config):
    # register an additional marker
    config.addinivalue_line(
        "markers", "env(name): mark test to run only on named environment"
    )


def pytest_runtest_setup(item: pytest.Function):
    config = item.config
    with_tox = config.getoption("--with-tox")
    
    if not with_tox:
        return
    
    envnames = [mark.args[0] for mark in item.iter_markers(name="env")]
    optional = os.environ.get("OPTIONAL_PACKAGES_AVAILABLE")
    
    if envnames:
        if not optional:
            pytest.skip("test requires env in {!r}".format(envnames))
            return
        
        for env in envnames:
            if env not in optional:
                pytest.skip("test requires env in {!r}".format(envnames))
                return
