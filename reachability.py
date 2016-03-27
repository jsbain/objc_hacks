# coding: utf-8
from objc_util import *

NSBundle.bundleWithPath_('/System/Library/PrivateFrameworks/SoftwareUpdateServices.framework').load()

def currentNetworkType():
	''' 0: none
	1: wifi
	2+: cellular'''
	netMon=ObjCClass('SUNetworkMonitor').sharedInstance()
	return netMon.currentNetworkType()
def main():
	networkType=currentNetworkType()
	assert networkType>0, 'Network Not Connected'
	if networkType>1:
		ok_to_continue=raw_input('Using cellular data. Continue downloading? [y/n]')
		assert ok_to_continue.lower()=='y', 'User Cancelled'
		
if __name__=='__main__':
	main()
