import logging
import click

from nile import deployments
from nile.common import is_alias
from nile.core.account import Account
from nile.nre import NileRuntimeEnvironment
from nile.utils import normalize_number

from nile_upgrades import common


@click.command()
@click.argument("signer", type=str)
@click.argument("proxy_address_or_alias", type=str)
@click.argument("contract_name", type=str)
@click.option(
    "--max_fee", nargs=1, help="Maximum fee for the transaction. Defaults to 0."
)
def upgrade_proxy(signer, proxy_address_or_alias, contract_name, max_fee=None):
    """
    Upgrade a proxy to a different implementation contract.

    SIGNER - private key alias for the Account to use.

    PROXY_ADDRESS_OR_ALIAS - the proxy address or alias.

    CONTRACT_NAME - the name of the implementation contract to upgrade to.
    """

    nre = NileRuntimeEnvironment()

    if not is_alias(proxy_address_or_alias):
        proxy_address_or_alias = normalize_number(proxy_address_or_alias)
    ids = deployments.load(proxy_address_or_alias, nre.network)
    id = next(ids, None)
    if id is None:
        raise Exception(
            f"Deployment with address or alias {proxy_address_or_alias} not found"
        )
    if next(ids, None) is not None:
        raise Exception(
            f"Multiple deployments found with address or alias {proxy_address_or_alias}"
        )

    proxy_address = id[0]

    impl_class_hash = common.declare_impl(nre, contract_name, signer, max_fee)

    logging.info(f"⏭️  Upgrading proxy {proxy_address} to class hash {impl_class_hash}")
    account = Account(signer, nre.network)
    upgrade_result = account.send(
        proxy_address, "upgrade", calldata=[impl_class_hash], max_fee=max_fee
    )

    tx_hash = _get_tx_hash(upgrade_result)
    logging.info(f"🧾 Upgrade transaction hash: {tx_hash}")

    deployments.update_abi(
        proxy_address, common.get_contract_abi(contract_name), nre.network
    )

    return tx_hash


def _get_tx_hash(output):
    lines = output.splitlines()
    for line in lines:
        if "Transaction hash" in line:
            return line.split(":")[1].strip()
