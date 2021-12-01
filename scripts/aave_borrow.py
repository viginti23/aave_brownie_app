from scripts.handy_funcs import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS
from brownie import config, network, interface
from scripts.get_weth import get_weth
from web3 import Web3

AMOUNT = Web3.toWei(0.1, 'ether')


# Approving ERC20 (WETH) transfer by interacting with ERC20 (WETH) contract's '.approve'
def approve_erc20(amount, spender, erc20_address, account):
    print('Approving ERC20 token...')
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print('Approved!')
    return True


def get_lending_pool():
    # Interfaces compile down to ABI
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config['networks'][network.show_active()]['lending_pool_addresses_provider'])
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool


def repay_all(amount, lending_pool, account):
    # approve ERC20
    approve_erc20(
        Web3.toWei(amount, 'ether'),
        lending_pool,
        config['networks'][network.show_active()]['dai_token'],
        account
    )
    repay_tx = lending_pool.repay(
        config['networks'][network.show_active()]['dai_token'],
        amount,
        1,
        account.address,
        {'from': account}
    )
    repay_tx.wait(1)
    print('Repaid!')


def get_asset_price(price_feed_address):
    # ABI
    # Address
    dai_eth_price_feed = interface.IAggregatorV3(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_latest_price = Web3.fromWei(latest_price, 'ether')
    print(f'The price of 1 DAI is {converted_latest_price} ETH.')
    return float(converted_latest_price)


def get_borrowable_data(lending_pool, account):
    # all data is returned in Wei
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        ltv,
        health_factor
    ) = lending_pool.getUserAccountData(account.address)
    total_collateral_eth = Web3.fromWei(total_collateral_eth, 'ether')
    total_debt_eth = Web3.fromWei(total_debt_eth, 'ether')
    available_borrow_eth = Web3.fromWei(available_borrow_eth, 'ether')
    print(f'You have {total_collateral_eth} worth of ETH deposited.')
    print(f'You have {total_debt_eth} worth of ETH borrowed in other tokens.')
    print(f'You can still borrow {available_borrow_eth} worth of ETH.')
    print(f'Current liquidation threshold is {current_liquidation_threshold} %.')
    print(f'Your ltv is {ltv}.')
    print(f'Your health factor is {health_factor}.')
    return float(available_borrow_eth), float(total_debt_eth)


def main():
    account = get_account()
    weth_gateway_contract_address = config[
        'networks'][network.show_active()]['weth_token']
    # if we have no WETH, call: (for example when we are testing on mainnet-fork)
    # get_weth()
    if network.show_active() in ['mainnet-fork']:
        get_weth()
    lending_pool = get_lending_pool()
    # Approve sending out ERC_20 tokens (WETHs)
    # spender = where we want our tokens to go (address type)
    approve_erc20(
        AMOUNT, lending_pool.address, weth_gateway_contract_address, account)
    print('Depositing...')
    tx = lending_pool.deposit(
        weth_gateway_contract_address, AMOUNT, account.address, 0, {'from': account})
    tx.wait(1)
    print('Deposited!')
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    print("Let's borrow!")
    # Assume we want to borrow some DAi => we need a price feed (e.g. from Chainlink)
    dai_in_eth_price = get_asset_price(
        config['networks'][network.show_active()]['dai_to_eth_price_feed'])
    amount_dai_to_borrow = (borrowable_eth * 0.95) * (1 / dai_in_eth_price)
    # borrowable_eth -> borrowable_dai * 95%
    print(f'We are going to borrow {amount_dai_to_borrow} DAI')
    # Now we borrow!
    dai_token_address = config['networks'][network.show_active()]['dai_token']
    print(f'Borrowing {amount_dai_to_borrow} DAI...')
    borrow_tx = lending_pool.borrow(
        dai_token_address, Web3.toWei(amount_dai_to_borrow, 'ether'), 1, 0, account.address, {'from': account})
    borrow_tx.wait(1)
    get_borrowable_data(lending_pool, account)
    print('Borrowed!')
    # repay_all(AMOUNT, lending_pool, account)
    print('You just deposited, borrowed and repaid!')
