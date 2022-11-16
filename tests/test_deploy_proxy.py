"""Tests for deploy proxy."""
import logging
from unittest.mock import patch

from nile_upgrades.deploy_proxy import deploy_proxy


NETWORK = "localhost"
CONTRACT = "contract"
SIGNER = "PKEY1"

SELECTOR = 1
CLASS_HASH = 16
ARG1 = "ABC"
ARG2 = 123
PROXY_ADDR = "0x000000000000000000000000000000000000000000000000000000000000000f"
PROXY_ADDR_INT = 15
PROXY_ABI = "path/proxy_abi.json"


@patch("nile_upgrades.common.declare_impl", return_value=CLASS_HASH)
@patch("starkware.starknet.compiler.compile.get_selector_from_name", return_value=1)
@patch("nile.nre.NileRuntimeEnvironment.deploy", return_value=(PROXY_ADDR_INT, PROXY_ABI))
def test_deploy_proxy(
    mock_deploy, mock_get_selector, mock_declare_impl, caplog
):
    logging.getLogger().setLevel(logging.DEBUG)

    result = deploy_proxy(SIGNER, CONTRACT, [ARG1, ARG2]);
    assert result == PROXY_ADDR_INT

    # TODO check called once with

    # check logs
    assert f"Proxy deployed to address {PROXY_ADDR} using ABI {PROXY_ABI}" in caplog.text
