# Layerzero BTC.b bridge farmer

This script move BTC.b token between Polygon-Avalanche networks. This is not a full combine for airdrop. The main purpose of this script is to keep regular activity by moving BTC.B between Polygon/Avalanche networks.

## Prerequisites

- Get native tokens for fee in Avalanche/Polygon for each account
- Buy BTC.b via TraderJoe swap and leave tokens in Avalanche or Polygon network.
- Add private keys to data.txt (one line - one key)


## Installation

Run commands like this:

```
apt install python3-pip, git
git clone https://github.com/Kizliak/layerzero-btcb-farmer
pip install -r requirements.txt
```

Edit config file with your values

```
nano config.py
```

Run script
```
python3 main.py
```
