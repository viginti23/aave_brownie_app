1. Swap ETH for WETH.

   How to get WETH?
    - interact with Aave WETHGateway contract (we need our script to be able to call deposit on the contract


2. Deposit some (W)ETH into Aave.
    - borrow, withdraw, repay, deposit by interacting LendingPool contract
    - Lending Pool contract:
        - address:
            - ABI and address of Lending Pool Addresses Provider:
                - address from Aave,
                - ABI through interface
        - ABI: through interface

3. Borrow some asset with the ETH collateral
    - Sell that borrowed asset (short selling)

4. Repay all back.

Integration test: Kovan

Unit test: mainnet-fork