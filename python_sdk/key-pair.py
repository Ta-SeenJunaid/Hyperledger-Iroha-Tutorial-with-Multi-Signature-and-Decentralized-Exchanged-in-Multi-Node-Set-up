import argparse

from iroha import IrohaCrypto


def read_args():
    parse = argparse.ArgumentParser(
        description="Generate Iroha ED25519-SHA3 Key-Pair"
    )
    parse.add_argument('--private_key', required=False,
                       help='Please provide Iroha ED25519-SHA3 private_key',
                       type=str)

    return parse.parse_args()


if __name__ == '__main__':
    args = read_args()

    if args.private_key:
        try:
            private_key = str.encode(args.private_key)
            public_key = IrohaCrypto.derive_public_key(private_key)
        except Exception as e:
            raise Exception(f'Failed to generate key-pair from given private key. {e}')

    else:
        private_key = IrohaCrypto.private_key()
        public_key = IrohaCrypto.derive_public_key(private_key)

    print("Private key: ")
    print(private_key.decode())
    print("Corresponding public key: ")
    print(public_key.decode())