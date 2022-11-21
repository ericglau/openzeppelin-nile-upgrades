from nile import deployments
from nile.common import (
    QUERY_VERSION,
    TRANSACTION_VERSION,
    is_alias,
    normalize_number,
)
from nile.core.call_or_invoke import call_or_invoke
from nile.deployments import normalize_number
from nile.utils.get_nonce import get_nonce_without_log as get_nonce


async def send_multicall(
    account,
    calls,
    nonce=None,
    max_fee=None,
    query_type=None,
    watch_mode=None,
):
    """Execute a multicall call for a tx going through an Account contract."""

    processed_calls = []

    for call in calls:
        assert len(call) == 3, "Invalid call parameters"

        address_or_alias = call[0]
        method = call[1]
        calldata = call[2]

        # get target address with the right format
        target_address = _get_target_address(account, address_or_alias)

        calldata = await _process_calldata(calldata)

        processed_calls.append([target_address, method, calldata])

    # process and parse arguments
    max_fee, nonce = await _process_arguments(
        account, max_fee, nonce
    )

    # get tx version
    tx_version = QUERY_VERSION if query_type else TRANSACTION_VERSION

    calldata, sig_r, sig_s = account.signer.sign_invoke(
        sender=account.address,
        calls=processed_calls,
        nonce=nonce,
        max_fee=max_fee,
        version=tx_version,
    )

    return await call_or_invoke(
        contract=account,
        type="invoke",
        method="__execute__",
        params=calldata,
        network=account.network,
        signature=[sig_r, sig_s],
        max_fee=max_fee,
        query_flag=query_type,
        watch_mode=watch_mode,
    )

def _get_target_address(account, address_or_alias):
    if not is_alias(address_or_alias):
        address_or_alias = normalize_number(address_or_alias)

    target_address, _ = (
        next(deployments.load(address_or_alias, account.network), None)
        or address_or_alias
    )

    return target_address

async def _process_arguments(self, max_fee, nonce):
    max_fee = 0 if max_fee is None else int(max_fee)

    if nonce is None:
        nonce = await get_nonce(self.address, self.network)

    return max_fee, nonce

async def _process_calldata(calldata=None):
    if calldata is not None:
        calldata = [normalize_number(x) for x in calldata]

    return calldata
