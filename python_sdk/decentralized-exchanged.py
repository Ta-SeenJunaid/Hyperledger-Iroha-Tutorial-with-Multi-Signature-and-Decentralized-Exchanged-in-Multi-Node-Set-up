#!/usr/bin/env python3
import time
import binascii
from iroha import  Iroha, IrohaGrpc, IrohaCrypto
import os
import sys


IROHA_HOST_ADDR_1 = os.getenv('IROHA_HOST_ADDR_1', '172.29.101.121')
IROHA_PORT_1 = os.getenv('IROHA_PORT_1', '50051')
IROHA_HOST_ADDR_2 = os.getenv('IROHA_HOST_ADDR_2', '172.29.101.122')
IROHA_PORT_2 = os.getenv('IROHA_PORT_2', '50052')
IROHA_HOST_ADDR_3 = os.getenv('IROHA_HOST_ADDR_2', '172.29.101.123')
IROHA_PORT_3 = os.getenv('IROHA_PORT_3', '50053')
ADMIN_ACCOUNT_ID = os.getenv('ADMIN_ACCOUNT_ID', 'admin@test')
ADMIN_PRIVATE_KEY = os.getenv(
    'ADMIN_PRIVATE_KEY', 'f101537e319568c765b2cc89698325604991dca57b9716b58016b253506cab70')

print("""
Please ensure about MST in iroha config file.
""")

if sys.version_info[0] < 3:
    raise Exception('Python 3 or more updated version is required.')

iroha_admin = Iroha(ADMIN_ACCOUNT_ID)
net_1 = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR_1, IROHA_PORT_1))
net_2 = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR_2, IROHA_PORT_2))
net_3 = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR_3, IROHA_PORT_3))

satoshi_private_key = IrohaCrypto.private_key()
satoshi_public_key = IrohaCrypto.derive_public_key(satoshi_private_key)
SATOSHI_ACCOUNT_ID = os.getenv('SATOSHI_ACCOUNT_ID', 'satoshi@test')
iroha_satoshi = Iroha(SATOSHI_ACCOUNT_ID)


nakamoto_private_key = IrohaCrypto.private_key()
nakamoto_public_key = IrohaCrypto.derive_public_key(nakamoto_private_key)
NAKAMOTO_ACCOUNT_ID = os.getenv('NAKAMOTO_ACCOUNT_ID', 'nakamoto@test')
iroha_nakamoto = Iroha(NAKAMOTO_ACCOUNT_ID)


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
    global net_1
    hex_hash = binascii.hexlify(IrohaCrypto.hash(transaction))
    print('Transaction hash = {}, creator = {}'.format(
        hex_hash, transaction.payload.reduced_payload.creator_account_id))
    net_1.send_tx(transaction)
    for status in net_1.tx_status_stream(transaction):
        print(status)


@trace
def send_batch_and_print_status(transactions):
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
    global iroha_admin
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
    init_tx = iroha_admin.transaction(init_cmds)
    IrohaCrypto.sign_transaction(init_tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(init_tx)


init_operation()








































