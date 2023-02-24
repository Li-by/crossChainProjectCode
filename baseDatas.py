# 数据获取时间截止到2022/08/31，3条链上的所有结束区块。
from web3 import Web3

baseData = {


'use_network' : {
				'ETH' : "https://api.infstones.com/ethereum/mainnet/1111111111111",
				'BSC' : 'https://bsc-dataseed1.binance.org/',
               'Polygon' : 'https://rpc-mainnet.maticvigil.com', #matic  1000的查找范围
               },

'crossChainProject' : {

	'multichain': #该项目总共有5个事件
		{
			'ETH' : {
						'deployAccount' : Web3.toChecksumAddress('0xfA9dA51631268A30Ec3DDd1CcBf46c65FAD99251'),
						'startBlock' : 12047165, #来自部署账户的第一笔交易
						'events' : {
										"anySwapIn" : "LogAnySwapIn(bytes32,address,address,uint256,uint256,uint256)",  #资产转入
										"anySwapOut1" : "LogAnySwapOut(address,address,address,uint256,uint256,uint256)", #转出
										"anySwapOut2" : "LogAnySwapOut(address,address,string,uint256,uint256,uint256)", #转出
										"tokensForTokens" : "LogAnySwapTradeTokensForTokens(address[],address,address,uint256,uint256,uint256,uint256)",
										"tokensForNative" : "LogAnySwapTradeTokensForNative(address[],address,address,uint256,uint256,uint256,uint256)",
									}
					},

			'BSC' : {
						'deployAccount' : Web3.toChecksumAddress('0xfA9dA51631268A30Ec3DDd1CcBf46c65FAD99251'),
						'startBlock' : 5900760,  #来自部署账户的第一笔交易
						'events' : {
										"anySwapIn" : "LogAnySwapIn(bytes32,address,address,uint256,uint256,uint256)",  #资产转入
										"anySwapOut1" : "LogAnySwapOut(address,address,address,uint256,uint256,uint256)", #转出
										"anySwapOut2" : "LogAnySwapOut(address,address,string,uint256,uint256,uint256)", #转出
										"tokensForTokens" : "LogAnySwapTradeTokensForTokens(address[],address,address,uint256,uint256,uint256,uint256)",
										"tokensForNative" : "LogAnySwapTradeTokensForNative(address[],address,address,uint256,uint256,uint256,uint256)",
									}
					},

			'Polygon' : {
						'deployAccount' : Web3.toChecksumAddress('0xfA9dA51631268A30Ec3DDd1CcBf46c65FAD99251'),
						'startBlock' : 11912470, #来自部署账户的第一笔交易
						'events' : {
										"anySwapIn" : "LogAnySwapIn(bytes32,address,address,uint256,uint256,uint256)",  #资产转入
										"anySwapOut1" : "LogAnySwapOut(address,address,address,uint256,uint256,uint256)", #转出
										"anySwapOut2" : "LogAnySwapOut(address,address,string,uint256,uint256,uint256)", #转出
										"tokensForTokens" : "LogAnySwapTradeTokensForTokens(address[],address,address,uint256,uint256,uint256,uint256)",
										"tokensForNative" : "LogAnySwapTradeTokensForNative(address[],address,address,uint256,uint256,uint256,uint256)",
									}
					},
		},

	'stargate' : 
		{
			'ETH' : {
					'deployAccount' : Web3.toChecksumAddress('0x1D7C6783328C145393e84fb47a7f7C548f5Ee28d'),
					'startBlock' : 14398654, #来自部署账户的第一笔交易
					# PolyWrapperLock(address indexed fromAsset, address indexed sender, uint64 toChainId, bytes toAddress, uint net, uint fee, uint id);
					'events' : {
									"Swap" : "Swap(uint16,uint256,address,uint256,uint256,uint256,uint256,uint256)",  #资产转入
								}
					},	

			'BSC' : {
					'deployAccount' : Web3.toChecksumAddress('0x1D7C6783328C145393e84fb47a7f7C548f5Ee28d'),
					'startBlock' : 16115384,  #来自部署账户的第一笔交易
					'events' : {
									"Swap" : "Swap(uint16,uint256,address,uint256,uint256,uint256,uint256,uint256)",  #资产转入
								}
					},

			'Polygon' : {
					'deployAccount' : Web3.toChecksumAddress('0x1D7C6783328C145393e84fb47a7f7C548f5Ee28d'),
					'startBlock' : 26031261, #来自部署账户的第一笔交易
					'events' : {
									"Swap" : "Swap(uint16,uint256,address,uint256,uint256,uint256,uint256,uint256)",  #资产转入
								}
					},

		},

	'poly' : 
		{
			'ETH' : {
					'deployAccount' : Web3.toChecksumAddress('0xeF86b2c8740518548ae449c4C3892B4be0475d8c'),
					'startBlock' : 11775151,  #13080014, #来自部署账户的第一笔交易
					# PolyWrapperLock(address indexed fromAsset, address indexed sender, uint64 toChainId, bytes toAddress, uint net, uint fee, uint id);
					'events' : {
									"Poly" : "PolyWrapperLock(address,address,uint64,bytes,uint256,uint256,uint256)",  #资产转入
								}
					},

			'BSC' : {
					'deployAccount' : Web3.toChecksumAddress('0xeF86b2c8740518548ae449c4C3892B4be0475d8c'),
					'startBlock' : 4498293,  #9905189,  #来自部署账户的第一笔交易
					'events' : {
									"Poly" : "PolyWrapperLock(address,address,uint64,bytes,uint256,uint256,uint256)",  #资产转入
								}
					},

			'Polygon' : {
					'deployAccount' : Web3.toChecksumAddress('0xeF86b2c8740518548ae449c4C3892B4be0475d8c'),
					'startBlock' : 17357102, #来自部署账户的第一笔交易
					'events' : {
									"Poly" : "PolyWrapperLock(address,address,uint64,bytes,uint256,uint256,uint256)",  #资产转入
								}
					},
		},

	'portal' : 
		{
			'ETH' : {
					'deployAccount' : Web3.toChecksumAddress('0x5B3899809Ae2c87FdA11280b7c61C06A5F4db1de'),
					'startBlock' : 12959534, #来自部署账户的第一笔交易
					# PolyWrapperLock(address indexed fromAsset, address indexed sender, uint64 toChainId, bytes toAddress, uint net, uint fee, uint id);
					'events' : {
									"Portal" : "LogMessagePublished(address,uint64,uint32,bytes,uint8)",  #资产转入
								},

					"funcs" : {
								"transferETH" : "wrapAndTransferETH(uint16,bytes32,uint256,uint32)",   # 0x9981509f
								"transferTokens" : "transferTokens(address,uint256,uint16,bytes32,uint256,uint32)", # 0x0f5287b0
								"transferETHPayload" : "wrapAndTransferETHWithPayload(uint16,bytes32,uint32,bytes)",  # '0xbee9cdfc'
								"transferTokensPayload" : "transferTokensWithPayload(address,uint256,uint16,bytes32,uint32,bytes)", # 0xc5a5ebda
								},
					},	


			'BSC' : {
					'deployAccount' : Web3.toChecksumAddress('0x5B3899809Ae2c87FdA11280b7c61C06A5F4db1de'),
					'startBlock' : 9744916,  #来自部署账户的第一笔交易
					'events' :  {
									"Portal" : "LogMessagePublished(address,uint64,uint32,bytes,uint8)",  #资产转入
									},
					"funcs" : {
								"transferETH" : "wrapAndTransferETH(uint16,bytes32,uint256,uint32)",   # 0x9981509f
								"transferTokens" : "transferTokens(address,uint256,uint16,bytes32,uint256,uint32)", # 0x0f5287b0
								"transferETHPayload" : "wrapAndTransferETHWithPayload(uint16,bytes32,uint32,bytes)",  # '0xbee9cdfc'
								"transferTokensPayload" : "transferTokensWithPayload(address,uint256,uint16,bytes32,uint32,bytes)", # 0xc5a5ebda
								},
					},

			'Polygon' : {
					'deployAccount' : Web3.toChecksumAddress('0x5B3899809Ae2c87FdA11280b7c61C06A5F4db1de'),
					'startBlock' : 20627919, #来自部署账户的第一笔交易
					'events' : {
									"Portal" : "LogMessagePublished(address,uint64,uint32,bytes,uint8)",  #资产转入
								},
					"funcs" : {
								"transferETH" : "wrapAndTransferETH(uint16,bytes32,uint256,uint32)",   # 0x9981509f
								"transferTokens" : "transferTokens(address,uint256,uint16,bytes32,uint256,uint32)", # 0x0f5287b0
								"transferETHPayload" : "wrapAndTransferETHWithPayload(uint16,bytes32,uint32,bytes)",  # '0xbee9cdfc'
								"transferTokensPayload" : "transferTokensWithPayload(address,uint256,uint16,bytes32,uint32,bytes)", # 0xc5a5ebda
								},
					},
		}

	}


}



"""
{   # tokenID 
     "eth" : 1,
     "Fantom" : 250,
     "bnb" : 56,
     polygon : 137,
}

token
{
     eth : 0x0615Dbba33Fe61a31c7eD131BDA6655Ed76748B1
}
"""