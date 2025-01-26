"""Test the main module."""

import sys

import pytest

from gazpar2mqtt import __main__


# ----------------------------------
@pytest.mark.asyncio
async def test_main():

    # Simulate command line arguments
    sys.argv = [
        "gazpar2mqtt",
        "-c",
        "tests/config/configuration.yaml",
        "-s",
        "tests/config/secrets.yaml",
    ]

    await __main__.main()
