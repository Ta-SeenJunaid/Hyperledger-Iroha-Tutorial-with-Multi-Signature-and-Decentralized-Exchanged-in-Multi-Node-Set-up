import binascii
from iroha import  Iroha, IrohaGrpc, IrohaCrypto
import os
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
iroha_admin = Iroha(ADMIN_ACCOUNT_ID)

# Satoshi's crypto material generation for account 1
satoshi_private_key_1 = IrohaCrypto.private_key()
satoshi_public_key_1 = IrohaCrypto.derive_public_key(satoshi_private_key_1)
SATOSHI_ACCOUNT_ID_1 = os.getenv('SATOSHI_ACCOUNT_ID_1', 'satoshi@test')
iroha_satoshi_1 = Iroha(SATOSHI_ACCOUNT_ID_1)

# Satoshi's crypto material generation for account 2
satoshi_private_key_2 = IrohaCrypto.private_key()
satoshi_public_key_2 = IrohaCrypto.derive_public_key(satoshi_private_key_2)
SATOSHI_ACCOUNT_ID_2 = os.getenv('SATOSHI_ACCOUNT_ID_2', 'satoshi@test')
iroha_satoshi_2 = Iroha(SATOSHI_ACCOUNT_ID_2)

# Nakamoto's crypto material generation
nakamoto_private_key = IrohaCrypto.private_key()
nakamoto_public_key = IrohaCrypto.derive_public_key(nakamoto_private_key)
# Nakamoto's account
NAKAMOTO_ACCOUNT_ID = os.getenv('NAKAMOTO_ACCOUNT_ID', 'nakamoto@test')
iroha_nakamoto = Iroha(NAKAMOTO_ACCOUNT_ID)


print("""
Please ensure about MST in iroha config file.
""")


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
    global net_1
    hex_hash = binascii.hexlify(IrohaCrypto.hash(transaction))
    print('Transaction hash = {}, creator = {}'.format(
        hex_hash, transaction.payload.reduced_payload.creator_account_id))
    net_1.send_tx(transaction)
    for status in net_1.tx_status_stream(transaction):
        print(status)


@trace
def send_batch_and_print_status(transactions):
    """
    send batch of transactions
    """
    global net_1
    net_1.send_txs(transactions)
    for tx in transactions:
        hex_hash = binascii.hexlify(IrohaCrypto.hash(tx))
        print('\t' + '-' * 20)
        print('Transaction hash = {}, creator = {}'.format(
            hex_hash, tx.payload.reduced_payload.creator_account_id))
        # for status in net_1.tx_status_stream(tx):
        #     print(status)


@trace
def init_operation():
    """
    Init operation with some initialization commands
    This operation is performed by Admin with 'admin@test' account
    and Admin's valid credentials
    """
    global iroha_admin
    '''
    1. Admin create 'scoin' asset at 'test' domain with precision=2
    2. Admin add '10000' ammount of scoin asset 
       where asset id is 'scoin#test'
    3. Admin create new account where account_name='satoshi',
       domain_id='test' with account holder public key
    4. Admin create new account where account_name='nakamoto',
       domain_id='test' with account holder public key
    5. Admin transfer '10000' amount of 'scoin' from 
       admin's account to 'satoshi' account        
    '''
    init_cmds = [
        iroha_admin.command('CreateAsset', asset_name='scoin',
                      domain_id='test', precision=2),
        iroha_admin.command('AddAssetQuantity',
                      asset_id='scoin#test', amount='10000'),
        iroha_admin.command('CreateAccount', account_name='satoshi', domain_id='test',
                      public_key=satoshi_public_key_1),
        iroha_admin.command('CreateAccount', account_name='nakamoto', domain_id='test',
                      public_key=nakamoto_public_key),
        iroha_admin.command('TransferAsset', src_account_id='admin@test', dest_account_id='satoshi@test',
                      asset_id='scoin#test', description='init top up', amount='10000'),
    ]
    '''
    Admin create transaction and sign with admin's private key
    Finally send the transaction to Iroha Peer
    '''
    init_tx = iroha_admin.transaction(init_cmds)
    IrohaCrypto.sign_transaction(init_tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(init_tx)


@trace
def add_keys_and_set_quorum():
    """
    Satoshi add keys for signatory and set quorum
    """
    global iroha_satoshi_1
    '''
    Signatory represents an entity that can confirm 
    multi signature transactions (MST) for an account.
    Quorum number is a minimum amount of signatures 
    required to consider a transaction signed. 
    Satoshi add new signatory with that entity's (Satoshi 2) public key.
    Satoshi set quorum number 2
    '''
    satoshi_cmds = [
        iroha_satoshi_1.command('AddSignatory', account_id='satoshi@test',
                                public_key=satoshi_public_key_2),
        iroha_satoshi_1.command('SetAccountQuorum',
                                account_id='satoshi@test', quorum=2)
    ]
    '''
    Satoshi create transaction and sign with satoshi's private key
    Finally send the transaction to Iroha Peer
    '''
    satoshi_tx = iroha_satoshi_1.transaction(satoshi_cmds)
    IrohaCrypto.sign_transaction(satoshi_tx, satoshi_private_key_1)
    send_transaction_and_print_status(satoshi_tx)


@trace
def multi_signature_transaction():
    '''
    Multi signature transaction where quorum > 1
    '''
    global iroha_satoshi_1
    global iroha_satoshi_2
    '''
    '10' amount of 'scoin' will be transferred 
    from 'satoshi' account to 'nakamoto' account  
    where quorum number is 2 
    '''
    multi_sign_tx = iroha_satoshi_1.transaction(
        [iroha_satoshi_1.command(
            'TransferAsset', src_account_id='satoshi@test', dest_account_id='nakamoto@test', asset_id='scoin#test',
            amount='10'
        )],
        creator_account='satoshi@test',
        quorum=2
    )
    '''
    Satoshi_1 sign the transaction with it's private key 
    '''
    IrohaCrypto.sign_transaction(multi_sign_tx, satoshi_private_key_1)
    '''
    Satoshi_2 can find pending transactions from peer if 
    Satoshi_1 sent that on peer (Like the example of decentralized exchanged)
    or Satoshi_1 may pass that via a messaging channel
    Satoshi_2 sign the transaction with it's private key     
    '''
    IrohaCrypto.sign_transaction(multi_sign_tx, satoshi_private_key_2)
    '''
    Finally send the transaction to Iroha Peer
    '''
    send_transaction_and_print_status(multi_sign_tx)


@trace
def get_satoshi_account_assets_from_peer_1():
    """
    Satoshi get account assets by querying
    from peer 1 with valid credentials
    """
    global net_1
    query = iroha_satoshi_1.query('GetAccountAssets', account_id='satoshi@test')
    IrohaCrypto.sign_query(query, satoshi_private_key_1)

    response = net_1.send_query(query)
    data = response.account_assets_response.account_assets
    for asset in data:
        print('Asset id = {}, balance = {}'.format(
            asset.asset_id, asset.balance))


@trace
def get_satoshi_account_assets_from_peer_2():
    """
    Satoshi get account assets by querying
    from peer 2 with valid credentials
    """
    global net_2
    query = iroha_satoshi_1.query('GetAccountAssets', account_id='satoshi@test')
    IrohaCrypto.sign_query(query, satoshi_private_key_1)

    response = net_2.send_query(query)
    data = response.account_assets_response.account_assets
    for asset in data:
        print('Asset id = {}, balance = {}'.format(
            asset.asset_id, asset.balance))


@trace
def get_satoshi_account_assets_from_peer_3():
    """
    Satoshi get account assets by querying
    from peer 3 with valid credentials
    """
    global net_3
    query = iroha_satoshi_1.query('GetAccountAssets', account_id='satoshi@test')
    IrohaCrypto.sign_query(query, satoshi_private_key_1)

    response = net_3.send_query(query)
    data = response.account_assets_response.account_assets
    for asset in data:
        print('Asset id = {}, balance = {}'.format(
            asset.asset_id, asset.balance))


@trace
def get_nakamoto_account_assets_from_peer_3():
    """
    Nakamoto get account assets by querying
    from peer 3 with valid credentials
    """
    global net_3
    query = iroha_nakamoto.query('GetAccountAssets', account_id='nakamoto@test')
    IrohaCrypto.sign_query(query, nakamoto_private_key)

    response = net_3.send_query(query)
    data = response.account_assets_response.account_assets
    for asset in data:
        print('Asset id = {}, balance = {}'.format(
            asset.asset_id, asset.balance))


init_operation()
add_keys_and_set_quorum()
multi_signature_transaction()
get_satoshi_account_assets_from_peer_1()
get_satoshi_account_assets_from_peer_2()
get_satoshi_account_assets_from_peer_3()
get_nakamoto_account_assets_from_peer_3()
