"""Test the main module."""

import sys

from gazpar2mqtt import __main__


# ----------------------------------
def test_main():

    # Simulate command line arguments
    sys.argv = [
        "gazpar2mqtt",
        "-c",
        "tests/config/configuration.yaml",
        "-s",
        "tests/config/secrets.yaml",
    ]

    __main__.main()
