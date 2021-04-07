#!/usr/bin/env python3
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
iroha_satoshi = Iroha(NAKAMOTO_ACCOUNT_ID)


def trace(func):
    """
    A decorator function for tracing begin/end execution
    """
    def tracer(*args, **kwargs):
        name = func.__name__
        print(f'\tEntering {name}')
        result = func(*args, **kwargs)
        print(f'\tLeaving {name}')
        return result

    return tracer()





























