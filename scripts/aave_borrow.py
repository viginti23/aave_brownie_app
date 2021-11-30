from scripts.handy_funcs import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS, FORKED_BLOCKCHAIN_ENVIRONMENTS
from brownie import config, network
from scripts.get_weth import get_weth


def main():
    account = get_account()
    erc20_address = config['networks'][network.show_active()]['weth_token']
    # if we have no WETH call:
    # get_weth()
    if network.show_active() in ['mainnet-fork']:
        get_weth()
    lending_pool = get_lending_pool()


def get_lending_pool():
    pass
