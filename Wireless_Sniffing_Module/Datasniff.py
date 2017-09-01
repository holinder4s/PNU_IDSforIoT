import hashlib
import hmac
import logging
import os
import struct
from binascii import a2b_hex, a2b_qp
from threading import Thread

from Crypto.Cipher import ARC4, AES
from pbkdf2 import PBKDF2
from scapy.all import *

logging.getLogger('scapy.runtime').setLevel(logging.ERRPR)

class DataSniffer:
	TUNSETIFF = 0x400454ca
	IFF_TAP = 0x0002
	IFF_NO_PI = 0x1000

	def __init__(self, wlan):
		self.wlan = wlan
		self.data_sniffing_thread = None
		self.sniff_fd = None
		self.deauth_list = []

	def start(self):
		## sniff parameter value check(target info)
		param_status = self.__param_check()
		if param_status != None:
			return param_status

		if not self.data_sniffing_thread:
			## change channel for sniffing AP & station's channel
			print "[+] Channel Setting : %s" % self.channel
			self.wlan.change_channel(self.channel)
		
			## Activate Tap Interface
			tap_status = self.__set_sniffing_interface()
			if tap_status != None:
				return tap_status
			self.data_sniffing_thread = DataSniffingThread(self)
			self.data_sniffing_thread.start()
	
	def stop(self):
		if self.data_sniffing_thread:
			self.data_sniffing_thread.exit()
			del self.data_sniffing_thread
			self.data_sniffing_thread = None

		if self.sniff_fd:
			os.close(self.sniff_fd)
			self.sniff_fd = None
		self.deauth_list = []

