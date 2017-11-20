import logging

import datetime

from app import *
from app import log, storage, node, transaction, util, key
from app.block import Block
from app.communicator import receiver, sender
from app.consensus.merkle_tree import merkle_tree, merkle_tree_2
from app.consensus.pow import proof_of_work
from app.node import Node
from app.transaction import Transaction

storage.init()


listen_thread = None


def initiate_node(*args):
	set_my_node()

	log.write("Start node")
	start_node()


'''
	Start Receiver Thread
	PORT: 10654
'''


def start_node():
	import threading
	global listen_thread
	listen_thread = threading.Thread(target=receiver.start, args=("Listener_Thread",
	                                                              util.get_ip_address('en0'), 3000))
	listen_thread.start()


def stop_node():
	storage.session.commit()
	storage.session.close()
	receiver.stop()
	global listen_thread
	listen_thread.join()


def create_block():
	transactions = transaction.get_transactions()

	# transaction이 없을 경우 block을 생성하지 않음
	if len(transactions) == 0:
		return

	# 내 node 가 가지고 있는 마지막 블럭
	last_block = block.get_last_block()

	# transaction JSON 문자열로 변환
	transactions_str = list(map(lambda x: x.to_json(), transactions))

	# transaction으로부터 merkle root 생성
	merkle_root = merkle_tree(transactions_str)

	# block 정보에 merkle root 할당
	block_info = merkle_root

	# block 새로 생성
	_block = Block()

	# 마지막 block이 있는 경우
	if last_block:
		# block 정보에 마지막 블럭의 해쉬를 더함
		block_info += last_block.block_hash

		# 새로 생성한 block에 이전 block 정보 저장
		_block.prev_block_hash = last_block.block_hash
		_block.prev_block_id = last_block.block_id

	# 작업 증명을 통해 nonce값과 hash 결과 생성
	hash_result, nonce = proof_of_work(block_info, diff_bits=5)

	# block 정보
	_block.block_hash = hash_result
	_block.nonce = nonce
	_block.block_info = block_info
	_block.time_stamp = datetime.datetime.now()

	# 내 node 에 block 저장
	block.create_block(_block)

	# 내 node가 가지고 있는 transaction 삭제
	transaction.remove_all()

	# 나머지 node에게 block 전송
	sender.send_to_all_node((_block.to_json()), except_my_node=True)

def list_all_node():
	for n in node.get_all():
		log.write(n, logging.DEBUG)


def list_all_transaction():
	for t in transaction.get_transactions():
		time_stamp = datetime.datetime.__str__(t.time_stamp)
		log.write(
			"\n++++++++++ Transaction ID: "+ t.tx_id +"++++++++++"
			"\nmessage: "+ t.message +
			"\ntype: "+ t.type +
			"\ntime_stamp: "+ time_stamp +
			"\npub_key: "+ t.pub_key +
			"\nsignature: "+ t.signature +
			"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++",
			logging.DEBUG)
		# log.write(t, logging.DEBUG)


def list_all_block():
	for b in block.get_all_block():
		time_stamp = datetime.datetime.__str__(b.time_stamp)
		log.write(
			"\n======================= Block ======================="
			"\nblock_hash: "+ b.block_hash +
			"\nprev_block_hash: "+ b.prev_block_hash +
			"\ntype: "+ b.type +
			"\ntime_stamp: "+ time_stamp +
			"\nnonce: "+ b.nonce +
			"\n=====================================================",
			logging.DEBUG)


def set_my_node():
	my_node = Node(util.get_ip_address('en0'))
	key.generate_key()
	log.write("Set my node")
	node.add_node(my_node)
