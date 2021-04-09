# Hyperledger-Iroha-Tutorial-with-Multi-Signature-and-Decentralized-Exchanged-in-Multi-Node-Set-up

## Prerequisites
We run this demo with Docker on Ubuntu machine.

To run the python code, you also need python3, pip3 and iroha python lirary.
Install the iroha python library with following command:
```
pip3 install iroha==0.0.5.5
```

## Network Setup
From projects root directory, run the following command to clear previous setup:
```
bash network.sh down
```
From projects root directory, run the following command to setup the network:
```
bash network.sh up
```

## Pyhthon Code Run

### Transaction Example
From projects root directory, run the following command to clear previous setup:
```
bash network.sh down
```
From projects root directory, run the following command to setup the network:
```
bash network.sh up
```
From projects root directory, run the following command for transaction example:
```
python3 python_sdk/tx-example.py
```

### Decentralized Exchanged
From projects root directory, run the following command to clear previous setup:
```
bash network.sh down
```
From projects root directory, run the following command to setup the network:
```
bash network.sh up
```
From projects root directory, run the following command for decentralized-exchanged example:
```
python3 python_sdk/decentralized-exchanged.py
```

### Multi Signature

From projects root directory, run the following command to clear previous setup:
```
bash network.sh down
```
From projects root directory, run the following command to setup the network:
```
bash network.sh up
```
From projects root directory, run the following command for multi-signature example:
```
python3 python_sdk/multi-signature.py
```