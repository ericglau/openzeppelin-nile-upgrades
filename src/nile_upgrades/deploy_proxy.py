import logging
import os
import click

from starkware.starknet.compiler.compile import get_selector_from_name

from nile.nre import NileRuntimeEnvironment

from nile_upgrades import common


@click.command()
@click.argument("signer", type=str)
@click.argument("contract_name", type=str)
@click.argument("initializer_args", nargs=-1, type=click.UNPROCESSED)
@click.option(
    "--initializer",
    nargs=1,
    default="initializer",
    help="Initializer function name. Defaults to 'initializer'",
)
@click.option("--alias", nargs=1, help="Unique identifier for your proxy.")
@click.option(
    "--max_fee", nargs=1, help="Maximum fee for the transaction. Defaults to 0."
)
def deploy_proxy(
    signer, contract_name, initializer_args, initializer, alias=None, max_fee=None
):
    """
    Deploy an upgradeable proxy for an implementation contract.

    SIGNER - private key alias for the Account to use.

    CONTRACT_NAME - the name of the implementation contract.

    INITIALIZER_ARGS - arguments for the initializer function.
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
    logging.debug(f"Proxy deployed to address {addr} using ABI {abi}")

    return addr


def _get_proxy_artifact_path():
    package = os.path.dirname(os.path.realpath(__file__))
    return (f"{package}/artifacts", f"{package}/artifacts/abis")
