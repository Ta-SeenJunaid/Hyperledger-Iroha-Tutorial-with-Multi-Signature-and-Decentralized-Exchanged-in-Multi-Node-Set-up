import time
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

# Satoshi's crypto material generation
satoshi_private_key = IrohaCrypto.private_key()
satoshi_public_key = IrohaCrypto.derive_public_key(satoshi_private_key)
# Satoshi's account
SATOSHI_ACCOUNT_ID = os.getenv('SATOSHI_ACCOUNT_ID', 'satoshi@test')
iroha_satoshi = Iroha(SATOSHI_ACCOUNT_ID)

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
    2. Admin create 'ncoin' asset at 'test' domain with precision=2
    3. Admin add '10000' ammount of scoin asset 
       where asset id is 'scoin#test'
    4. Admin add '20000' ammount of ncoin asset 
       where asset id is 'ncoin#test'
    5. Admin create new account where account_name='satoshi',
       domain_id='test' with account holder public key
    6. Admin create new account where account_name='nakamoto',
       domain_id='test' with account holder public key
    7. Admin transfer '10000' amount of 'scoin' from 
       admin's account to 'satoshi' account
    8. Admin transfer '20000' amount of 'ncoin' from 
       admin's account to 'nakamoto' account         
    '''
    init_cmds = [
        iroha_admin.command('CreateAsset', asset_name='scoin',
                      domain_id='test', precision=2),
        iroha_admin.command('CreateAsset', asset_name='ncoin',
                      domain_id='test', precision=2),
        iroha_admin.command('AddAssetQuantity',
                      asset_id='scoin#test', amount='10000'),
        iroha_admin.command('AddAssetQuantity',
                      asset_id='ncoin#test', amount='20000'),
        iroha_admin.command('CreateAccount', account_name='satoshi', domain_id='test',
                      public_key=satoshi_public_key),
        iroha_admin.command('CreateAccount', account_name='nakamoto', domain_id='test',
                      public_key=nakamoto_public_key),
        iroha_admin.command('TransferAsset', src_account_id='admin@test', dest_account_id='satoshi@test',
                      asset_id='scoin#test', description='init top up', amount='10000'),
        iroha_admin.command('TransferAsset', src_account_id='admin@test', dest_account_id='nakamoto@test',
                      asset_id='ncoin#test', description='init top up', amount='20000')
    ]
    '''
    Admin create transaction and sign with admin's private key
    Finally send the transaction to Iroha Peer
    '''
    init_tx = iroha_admin.transaction(init_cmds)
    IrohaCrypto.sign_transaction(init_tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(init_tx)

@trace
def satoshi_creates_exchange_batch():
    """
    Satoshi creates decentralized exchanged branch
    """
    global iroha_satoshi
    global iroha_nakamoto
    '''
    '100' amount of 'scoin' will be transferred 
    from 'satoshi' account to 'nakamoto' account   
    '''
    satoshi_tx = iroha_satoshi.transaction(
        [iroha_satoshi.command(
            'TransferAsset', src_account_id='satoshi@test', dest_account_id='nakamoto@test', asset_id='scoin#test',
            amount='100'
        )],
        creator_account='satoshi@test'
    )
    '''
    '200' amount of 'ncoin' will be transferred 
    from 'nakamoto' account to 'satoshi' account   
    '''
    nakamoto_tx = iroha_nakamoto.transaction(
        [iroha_nakamoto.command(
            'TransferAsset', src_account_id='nakamoto@test', dest_account_id='satoshi@test', asset_id='ncoin#test',
            amount='200'
        )],
        creator_account='nakamoto@test'
    )
    '''
    Creating the batch of transactions for sending several transactions
    This is atomic batch which means each and every transaction must 
    need to pass all type of validations and after that all the transactions
    of this batch will commit transactional changes into leger. 
    '''
    iroha_satoshi.batch([satoshi_tx, nakamoto_tx], atomic=True)
    '''
    Satoshi sign only his transaction with his private key
    '''
    IrohaCrypto.sign_transaction(satoshi_tx, satoshi_private_key)
    '''
    Finally send the atomic batch of transactions to Iroha Peer
    '''
    send_batch_and_print_status([satoshi_tx, nakamoto_tx])
    time.sleep(10)


@trace
def nakamoto_accepts_exchange_request():
    """
    Nakomoto accepts  the atomic batch of transactions
    """
    global net_1
    '''
    Nakamoto can find pending transactions from peer 
    or Satoshi may pass that via a messaging channel
    (Like the example of multi signature)
    Nakamoto is querying pending transactions from peer
    with his valid credentials
    '''
    q = IrohaCrypto.sign_query(
        iroha_nakamoto.query('GetPendingTransactions'),
        nakamoto_private_key
    )
    '''
    The atomic batch of transactions, which was previously created by 
    Satoshi are now in pending state as those got Satoshi's signature for 
    transferring of '100' amount of 'scoin'  from 'satoshi' account to 
    'nakamoto' account but do not get Nakamoto's signature for transferring 
    of '200' amount of 'ncoin' from  'nakamoto' account to 'satoshi' account
    '''
    pending_transactions = net_1.send_query(q)
    '''
    This atomic batch of pending transactions, already 
    got Satoshi's signature and only need Nakamoto's signature
    Nakamoto will delete Satoshi's signature and will sign 
    only his transaction with his private key
    '''
    for tx in pending_transactions.transactions_response.transactions:
        if tx.payload.reduced_payload.creator_account_id == 'satoshi@test':
            del tx.signatures[:]
        else:
            IrohaCrypto.sign_transaction(tx, nakamoto_private_key)
    '''
    Finally send the atomic batch of transactions to Iroha Peer
    '''
    send_batch_and_print_status(
        pending_transactions.transactions_response.transactions)
    time.sleep(10)


@trace
def check_no_pending_txs():
    """
    The atomic batch of transactions got all the necessary
    signatures and all the transactional changes are committed
    into the ledger. So there will be no pending transactions
    """
    global net_1
    print(' ~~~ No pending txs expected:')
    print(
        net_1.send_query(
            IrohaCrypto.sign_query(
                iroha_nakamoto.query('GetPendingTransactions',
                            creator_account='nakamoto@test'),
                nakamoto_private_key
            )
        )
    )
    print(' ~~~')


@trace
def get_nakamoto_account_assets_from_peer_1():
    """
    Nakamoto get account assets by querying
    from peer 1 with valid credentials
    """
    global net_1
    query = iroha_nakamoto.query('GetAccountAssets', account_id='nakamoto@test')
    IrohaCrypto.sign_query(query, nakamoto_private_key)

    response = net_1.send_query(query)
    data = response.account_assets_response.account_assets
    for asset in data:
        print('Asset id = {}, balance = {}'.format(
            asset.asset_id, asset.balance))


@trace
def get_nakamoto_account_assets_from_peer_2():
    """
    Nakamoto get account assets by querying
    from peer 2 with valid credentials
    """
    global net_2
    query = iroha_nakamoto.query('GetAccountAssets', account_id='nakamoto@test')
    IrohaCrypto.sign_query(query, nakamoto_private_key)

    response = net_2.send_query(query)
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


@trace
def get_satoshi_account_assets_from_peer_3():
    """
    Satoshi get account assets by querying
    from peer 3 with valid credentials
    """
    global net_3
    query = iroha_satoshi.query('GetAccountAssets', account_id='satoshi@test')
    IrohaCrypto.sign_query(query, satoshi_private_key)

    response = net_3.send_query(query)
    data = response.account_assets_response.account_assets
    for asset in data:
        print('Asset id = {}, balance = {}'.format(
            asset.asset_id, asset.balance))


init_operation()
satoshi_creates_exchange_batch()
nakamoto_accepts_exchange_request()
check_no_pending_txs()
get_nakamoto_account_assets_from_peer_1()
get_nakamoto_account_assets_from_peer_2()
get_nakamoto_account_assets_from_peer_3()
get_satoshi_account_assets_from_peer_3()
