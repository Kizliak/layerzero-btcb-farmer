import json
import time
import sys
from eth_account import Account
from web3 import Web3
from config import *
from decimal import Decimal

'''
# Layerzero-btcb-farm script by @Pearlsome https://t.me/legalcrypt
Script is
Topup account for atleast 1 MATIC + 0.1 AVAX (use bungee refuel https://bungee.exchange/refuel) + 0.00009 BTC.b (buy here https://traderjoexyz.com/avalanche/trade)
'''

def transaction_verification(transaction_hash, w3, network, txType):
    try:
        transaction_data = w3.eth.wait_for_transaction_receipt(transaction_hash, timeout=600)
        if transaction_data.get('status') != None and transaction_data.get('status') == 1:
            if network == "Avalanche":
                print(f'{txType} success: {scanAvax}{transaction_hash.hex()}')
            else:
                print(f'{txType} success: {scanPolygon}{transaction_hash.hex()}')
            return True
        else:
            if network == "Avalanche":
                print(f'{transaction_data.get("from")} | {txType} error: {transaction_data.get("transactionHash").hex()} {scanAvax}{transaction_hash.hex()}')
            else:
                print(f'{transaction_data.get("from")} | {txType} error: {transaction_data.get("transactionHash").hex()} {scanPolygon}{transaction_hash.hex()}')
            return False
    except Exception as e:
        print(f'{transaction_hash.hex()} | Transaction error: {e}')
        return False

def bridgeAvaxToPolygon(private_key, w3, btcAvaxBalance, fee):
    network = "Avalanche"
    account = w3.eth.account.from_key(private_key)
    address = account.address
    to_prefix = "0x000000000000000000000000"
    to_suffix = address[2:]
    _toAddress = to_prefix + to_suffix
    _dstChainId = 109
    _toAddress = "0x" + address[2:].rjust(64, '0').lower()
    _amount = int(btcAvaxBalance)
    _minAmount = int(btcAvaxBalance)
    _refundAddress = address
    _zroPaymentAddress = "0x0000000000000000000000000000000000000000"
    byted = bytes.fromhex(address[2:])
    byted_hex = byted.hex()
    _adapterParams = "0x0002000000000000000000000000000000000000000000000000000000000003d0900000000000000000000000000000000000000000000000000000000000000000" + byted_hex
    _callParams = {
        "refundAddress": address,
        "zroPaymentAddress": '0x0000000000000000000000000000000000000000',
        "adapterParams": _adapterParams
    }
    contract_address = Web3.toChecksumAddress(btcBridgeContractAddress)
    contract_data = w3.eth.contract(address=contract_address, abi=sendTo_avaxABI)
    nonce = w3.eth.get_transaction_count(address)
    txData = contract_data.encodeABI(fn_name="sendFrom", args=[address, _dstChainId, _toAddress, _amount, _minAmount, (_refundAddress, _zroPaymentAddress, _adapterParams)])
    tx = {
        "chainId": 43114,
        "to": contract_address,
        "value": fee
        "type": 2,
        "gas": 280000,
        'maxFeePerGas': 40000000000,
        'maxPriorityFeePerGas': 2000000000,
        #'gas': contract_data.functions.sendFrom(address, _dstChainId, _toAddress, _amount, _minAmount, (_refundAddress, _zroPaymentAddress, _adapterParams)).estimateGas()
        'from': address,
        "data": txData,
        "nonce": nonce
    }
    try:
        signed_transaction = account.sign_transaction(tx)
        transaction_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        txType = "Bridge"
        status = transaction_verification(transaction_hash, w3, network, txType)
        return status
    except:
        print('Bridge functiion fail!')
        return False
    
def bridgePolygonToAvax(private_key, w3, btcPolygonBalance):
    network = "Polygon"
    account = w3.eth.account.from_key(private_key)
    address = account.address
    to_prefix = "0x000000000000000000000000"
    to_suffix = address[2:]
    _toAddress = to_prefix + to_suffix
    _dstChainId = 106
    _toAddress = "0x" + address[2:].rjust(64, '0').lower()
    _amount = int(btcPolygonBalance)
    _minAmount = int(btcPolygonBalance)
    _refundAddress = address
    _zroPaymentAddress = "0x0000000000000000000000000000000000000000"
    byted = bytes.fromhex(address[2:])
    byted_hex = byted.hex()
    _adapterParams = "0x0002000000000000000000000000000000000000000000000000000000000003d0900000000000000000000000000000000000000000000000000000000000000000" + byted_hex
    _callParams = {
        "refundAddress": address,
        "zroPaymentAddress": '0x0000000000000000000000000000000000000000',
        "adapterParams": _adapterParams
    }
    contract_address = Web3.toChecksumAddress(btcBridgeContractAddress)
    contract_data = w3.eth.contract(address=contract_address, abi=sendTo_polygonABI)
    nonce = w3.eth.get_transaction_count(address)
    txData = contract_data.encodeABI(fn_name="sendFrom", args=[address, _dstChainId, _toAddress, _amount, _minAmount, (_refundAddress, _zroPaymentAddress, _adapterParams)])
    tx = {
        "chainId": 137,
        "to": contract_address,
        "value": Web3.toWei(0.25, "ether"),
        "gas": 250000,
        "gasPrice": w3.eth.gasPrice,
        'from': address,
        "data": txData,
        "nonce": nonce
    }
    try:
        signed_transaction = account.sign_transaction(tx)
        transaction_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        txType = "Bridge"
        status = transaction_verification(transaction_hash, w3, network, txType)
        return status
    except:
        print('Bridge functiion fail')
        return False
        
def setAllowance(private_key, w3, contract_data, network):
    account = w3.eth.account.from_key(private_key)
    address = account.address
    txData = contract_data.encodeABI(fn_name="approve", args=[Web3.toChecksumAddress(btcBridgeContractAddress), 400000000 ])
    nonce = w3.eth.get_transaction_count(address)
    if network == "Avalanche":
        contract_address = Web3.toChecksumAddress(btcAvaxTokenContract)
        tx = {
            "chainId": 43114,
            "to": contract_address,
            "value": 0,
            "type": 2,
            'maxFeePerGas': 40000000000,
            'maxPriorityFeePerGas': 2000000000,
            'gas': 60000,
            'from': address,
            "data": txData,
            "nonce": nonce
        }
    else:
        contract_address = Web3.toChecksumAddress(btcPolygonTokenContract)
        tx = {
            "chainId": 137,
            "to": contract_address,
            "value": 0,
            "gas": 60000,
            "gasPrice": w3.eth.gasPrice,
            'from': address,
            "data": txData,
            "nonce": nonce
        }
    try:
        signed_transaction = account.sign_transaction(tx)
        transaction_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        txType = "Approval"
        status = transaction_verification(transaction_hash, w3, network, txType)
        time.sleep(5)
        return status
    except:
        print('Approval function fail!')
        return False

def checkBTCallowance(private_key, w3, btcBalance, network):
    account = w3.eth.account.from_key(private_key)
    address = account.address
    if network == "Avalanche":
        contract_address = Web3.toChecksumAddress(btcAvaxTokenContract)
        contract_data = w3.eth.contract(address=contract_address, abi=btcAvaxABI)
        allowance = contract_data.functions.allowance(Web3.toChecksumAddress(address), Web3.toChecksumAddress(btcBridgeContractAddress)).call()
    else:
        contract_address = Web3.toChecksumAddress(btcPolygonTokenContract)
        contract_data = w3.eth.contract(address=contract_address, abi=btcPolygonABI)
        allowance = contract_data.functions.allowance(Web3.toChecksumAddress(address), Web3.toChecksumAddress(btcBridgeContractAddress)).call()
    print(f"Allowance: {allowance}")
    if allowance < btcBalance: setAllowance(private_key, w3, contract_data, network)

def main(row):
    private_key = row
    
    # Check Avax chain balance
    w3 = Web3(Web3.HTTPProvider(avaxRPC))
    account = w3.eth.account.from_key(private_key)
    address = account.address
    avaxBalance = w3.fromWei(w3.eth.getBalance(address), 'ether')
    btcAvaxTokenAddress = Web3.toChecksumAddress(btcAvaxTokenContract)
    btcAvaxToken = w3.eth.contract(address=btcAvaxTokenAddress, abi=btcAvaxABI)
    
    # Check Polygon chain balance
    m3 = Web3(Web3.HTTPProvider(polygonRPC))
    maticBalance = m3.fromWei(m3.eth.getBalance(address), 'ether')
    btcPolygonTokenAddress = Web3.toChecksumAddress(btcPolygonTokenContract)
    btcPolygonToken = m3.eth.contract(address=btcPolygonTokenAddress, abi=btcPolygonABI)
    btcAvaxBalance = Decimal(btcAvaxToken.functions.balanceOf(address).call() / 100000000)
    btcPolygonBalance = Decimal(btcPolygonToken.functions.balanceOf(address).call() / 100000000)
    
    # Choose target chain and send TX
    if (btcAvaxBalance > Decimal(minBTCbalance) and Decimal(avaxBalance) > Decimal(0.04)):
        print(f"==> \033[92m{address}\033[0m checking fee {'%.6f'%(btcAvaxBalance)} BTC.b from Avalanche to Polygon...")
        contract_address = Web3.toChecksumAddress(btcBridgeContractAddress)
        contract_data = w3.eth.contract(address=contract_address, abi=sendTo_avaxABI)
        zroPaymentAddress = "0x0000000000000000000000000000000000000000"
        byted = bytes.fromhex(address[2:])
        byted_hex = byted.hex()
        _adapterParams = "0x0002000000000000000000000000000000000000000000000000000000000003d09000000000000000000000000000000000000000000000000000" + byted_hex
        fees = contract_data.functions.estimateSendFee(109,
                                                                            address,
                                                                            btcAvaxToken.functions.balanceOf(address).call(),
                                                                            True,
                                                                            _adapterParams
                                                                            ).call()

        fee = int(fees[0])# /100 * 105
        print(w3.fromWei(fee, 'ether'))
        print(f"==> \033[92m{address}\033[0m sending {'%.6f'%(btcAvaxBalance)} BTC.b from Avalanche to Polygon...")
        checkBTCallowance(private_key, w3, btcAvaxBalance * 100000000, "Avalanche")
        time.sleep(1)
        if bridgeAvaxToPolygon(private_key, w3, btcAvaxBalance * 100000000, fee):
            print(f"Waiting delay before continue: ")
            for remaining in range(delayBetweenTX, 0, -1):
                sys.stdout.write("\r")
                sys.stdout.write("{:2d} seconds left.".format(remaining))
                sys.stdout.flush()
                time.sleep(1)
        else:
            time.sleep(1)
    elif (btcPolygonBalance > Decimal(minBTCbalance) and Decimal(maticBalance) > Decimal(0.4)):
        print(f"==> \033[92m{address}\033[0m checking fee {'%.6f'%(btcPolygonBalance)} BTC.b from Polygon to Avalanche...")
        contract_address = Web3.toChecksumAddress(btcBridgeContractAddress)
        contract_data = m3.eth.contract(address=contract_address, abi=sendTo_polygonABI)
        zroPaymentAddress = "0x0000000000000000000000000000000000000000"
        byted = bytes.fromhex(address[2:])
        byted_hex = byted.hex()
        _adapterParams = "0x0002000000000000000000000000000000000000000000000000000000000003d0900000000000000000000000000000000000000000000000000000000000000000" + byted_hex
        fees = contract_data.functions.estimateSendFee(106,
                                                                    address,
                                                                    btcPolygonToken.functions.balanceOf(address).call(),
                                                                    True,
                                                                    _adapterParams
                                                                    ).call()
        fee = fees[0]
        print(w3.fromWei(fee, 'ether'))
        print(f"==> \033[92m{address}\033[0m sending {'%.6f'%(btcPolygonBalance)} BTC.b from Polygon to Avalanche...")
        checkBTCallowance(private_key, m3, btcPolygonBalance * 100000000, "Polygon")
        time.sleep(1)
        if bridgePolygonToAvax(private_key, m3, btcPolygonBalance * 100000000):
            print(f"Waiting delay before continue: ")
            for remaining in range(delayBetweenTX, 0, -1):
                sys.stdout.write("\r")
                sys.stdout.write("{:2d} seconds left.".format(remaining))
                sys.stdout.flush()
                time.sleep(1)
                #print(f"Waiting {delayBetweenTX} seconds before continue...")
                #time.sleep(delayBetweenTX)
        else:
            time.sleep(1)
    else:
        print(f"Fail. Check balances ==> \033[92m{address}\033[0m:")
        print(f"==================== \033[0m {'%.2f'%(avaxBalance)} AVAX")
        print(f"==================== \033[0m {'%.2f'%(maticBalance)} MATIC")
        print(f"==================== \033[0m {'%.6f'%(btcAvaxBalance)} BTC.b on Avalanche")
        print(f"==================== \033[0m {'%.6f'%(btcPolygonBalance)} BTC.b on Polygon")


f = open('data.txt', 'r')
data = f.readlines()
f.close()
print("")
for row in data:
    main(row.strip())
    print("")