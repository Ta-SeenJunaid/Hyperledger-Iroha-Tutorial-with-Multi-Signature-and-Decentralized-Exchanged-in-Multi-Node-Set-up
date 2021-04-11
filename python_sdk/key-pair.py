#!/usr/bin/env python3
from iroha import IrohaCrypto

private_key = IrohaCrypto.private_key()
public_key = IrohaCrypto.derive_public_key(private_key)

print("Private key: ")
print(str(private_key)[2:-1])
print("Corresponding public key: ")
print(str(public_key)[2:-1])