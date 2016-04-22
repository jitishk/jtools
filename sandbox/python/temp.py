#!/usr/bin/python


import paramiko
import getpass


user = "test"
pswd = getpass.getpass()
hostname = "sjl3-ecp-ssr13"
hostip = "10.126.142.14"
hostname = "sjl3-ecp-ssr13"
hostip = "10.126.142.14"
hostname = "sjl3-ecp-ssr12"
hostip = "10.126.142.13"

ssh = paramiko.SSHClient()
ssh.Connect(hostip, username=user, password=pswd)
