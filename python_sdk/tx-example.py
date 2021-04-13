import os
import binascii
from iroha import IrohaCrypto
from iroha import Iroha, IrohaGrpc
import sys

if sys.version_info[0] < 3:
    raise Exception('Python 3 or more updated version is required.')


# Iroha peer 1
IROHA_HOST_ADDR_1 = os.getenv('IROHA_HOST_ADDR_1', '172.29.101.121')
IROHA_PORT_1 = os.getenv('IROHA_PORT_1', '50051')
# Iroha peer 2
IROHA_HOST_ADDR_2 = os.getenv('IROHA_HOST_ADDR_2', '172.29.101.122')
IROHA_PORT_2 = os.getenv('IROHA_PORT_2', '50052')
# Iroha peer 3
IROHA_HOST_ADDR_3 = os.getenv('IROHA_HOST_ADDR_2', '172.29.101.123')
IROHA_PORT_3 = os.getenv('IROHA_PORT_3', '50053')

# IrohaGrpc net for peer 1, 2, 3
net_1 = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR_1, IROHA_PORT_1))
net_2 = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR_2, IROHA_PORT_2))
net_3 = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR_3, IROHA_PORT_3))

# Admin Account loading with Admin's private key
ADMIN_PRIVATE_KEY = os.getenv(
    'ADMIN_PRIVATE_KEY', 'f101537e319568c765b2cc89698325604991dca57b9716b58016b253506cab70')
# Admin's account
ADMIN_ACCOUNT_ID = os.getenv('ADMIN_ACCOUNT_ID', 'admin@test')
iroha = Iroha(ADMIN_ACCOUNT_ID)



def trace(func):
    """
    A decorator for tracing methods' begin/end execution points
    """

    def tracer(*args, **kwargs):
        name = func.__name__
        print('\tEntering "{}"'.format(name))
        result = func(*args, **kwargs)
        print('\tLeaving "{}"'.format(name))
        return result

    return tracer

@trace
def send_transaction_and_print_status(transaction):
    """
    Send transaction and print status
    """
    hex_hash = binascii.hexlify(IrohaCrypto.hash(transaction))
    print('Transaction hash = {}, creator = {}'.format(
        hex_hash, transaction.payload.reduced_payload.creator_account_id))
    net_1.send_tx(transaction)
    for status in net_1.tx_status_stream(transaction):
        print(status)

@trace
def create_asset():
    """
    Creates asset 'coolcoin#test' with precision 2
    """
    commands = [
        iroha.command('CreateAsset', asset_name='coolcoin',
                      domain_id='test', precision=2)
    ]
    tx = IrohaCrypto.sign_transaction(
        iroha.transaction(commands), ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)

@trace
def add_coin_to_admin():
    """
    Add 1000.00 units of 'coolcoin#test' to 'admin@test'
    """
    tx = iroha.transaction([
        iroha.command('AddAssetQuantity',
                      asset_id='coolcoin#test', amount='1000.00')
    ])
    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)

@trace
def transfer_coin_from_admin_to_test_user():
    """
    Transfer 200.45 'coolcoin#test' from 'admin@test' to 'test@test'
    """
    tx = iroha.transaction([
        iroha.command('TransferAsset', src_account_id='admin@test', dest_account_id='test@test',
                      asset_id='coolcoin#test', description='Sending colcoin', amount='200.45')
    ])
    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)

@trace
def get_account_assets_from_peer_1():
    """
    List all the assets of 'admin@test'
    """
    query = iroha.query('GetAccountAssets', account_id='admin@test')
    IrohaCrypto.sign_query(query, ADMIN_PRIVATE_KEY)

    response = net_1.send_query(query)
    data = response.account_assets_response.account_assets
    for asset in data:
        print('Asset id = {}, balance = {}'.format(
            asset.asset_id, asset.balance))

@trace
def get_account_assets_from_peer_2():
    """
    List all the assets of 'admin@test'
    """
    query = iroha.query('GetAccountAssets', account_id='admin@test')
    IrohaCrypto.sign_query(query, ADMIN_PRIVATE_KEY)

    response = net_2.send_query(query)
    data = response.account_assets_response.account_assets
    for asset in data:
        print('Asset id = {}, balance = {}'.format(
            asset.asset_id, asset.balance))

@trace
def get_account_assets_from_peer_3():
    """
    List all the assets of 'admin@test'
    """
    query = iroha.query('GetAccountAssets', account_id='admin@test')
    IrohaCrypto.sign_query(query, ADMIN_PRIVATE_KEY)

    response = net_3.send_query(query)
    data = response.account_assets_response.account_assets
    for asset in data:
        print('Asset id = {}, balance = {}'.format(
            asset.asset_id, asset.balance))


create_asset()
add_coin_to_admin()
transfer_coin_from_admin_to_test_user()
get_account_assets_from_peer_1()
get_account_assets_from_peer_2()
get_account_assets_from_peer_3()