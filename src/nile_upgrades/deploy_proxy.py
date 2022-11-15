import logging
import os

from starkware.starknet.compiler.compile import get_selector_from_name

from nile.nre import NileRuntimeEnvironment
from nile.utils import hex_address

from nile_upgrades import common


def deploy_proxy(
    signer, contract_name, initializer_args, initializer='initializer', alias=None, max_fee=None, standalone_mode=None
):
    """
    Deploy an upgradeable proxy for an implementation contract.

    signer - private key alias for the Account to use.

    contract_name - the name of the implementation contract.

    initializer_args - array of arguments for the initializer function.

    initializer - initializer function name. Defaults to 'initializer'

    alias - Unique identifier for your proxy.

    max_fee - Maximum fee for the transaction. Defaults to 0.
    """

    nre = NileRuntimeEnvironment()

    impl_class_hash = common.declare_impl(nre, contract_name, signer, max_fee)

    logging.debug(f"Deploying upgradeable proxy...")
    selector = get_selector_from_name(initializer)
    addr, abi = nre.deploy(
        "Proxy",
        arguments=[impl_class_hash, selector, len(initializer_args), *initializer_args],
        alias=alias,
        overriding_path=_get_proxy_artifact_path(),
        abi=common.get_contract_abi(contract_name),
    )
    logging.debug(f"Proxy deployed to address {hex_address(addr)} using ABI {abi}")

    return addr


def _get_proxy_artifact_path():
    package = os.path.dirname(os.path.realpath(__file__))
    return (f"{package}/artifacts", f"{package}/artifacts/abis")
