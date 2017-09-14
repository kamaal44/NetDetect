"""
test config

Configuration file for testing models.
"""

import os
DATA_DIR = os.path.dirname(os.path.realpath(__file__)) + "/dumps/"

TF_SAVE = "iscx.tfrecords"
TEST_SAVE = "testing_set.csv"
TEST_URL = "https://nyc3.digitaloceanspaces.com/homearchive/testing.csv?AWSAccessKeyId=XF3ED5IAPT7JR6UA6NCB&Expires=1505337450&Signature=uXOTxOWQwnAdgljo0hrdj0XqXMs%3D"
TRAIN_SAVE = "training_set.csv"
TRAIN_URL = "https://nyc3.digitaloceanspaces.com/homearchive/training.csv?AWSAccessKeyId=XF3ED5IAPT7JR6UA6NCB&Expires=1505337468&Signature=Jewu5EgHi98IfeTnWJC1rVFmsLA%3D"

N_PACKETS = 20
N_FLOWS = 11
MALICIOUS_IPS = ["192.168.2.112", "131.202.243.84", "192.168.5.122", "198.164.30.2", "192.168.2.110", "192.168.5.122", "192.168.4.118", "192.168.5.122", "192.168.2.113", "192.168.5.122", "192.168.1.103", "192.168.5.122", "192.168.4.120", "192.168.5.122", "192.168.2.112", "192.168.2.110", "192.168.2.112", "192.168.4.120", "192.168.2.112", "192.168.1.103", "192.168.2.112", "192.168.2.113", "192.168.2.112", "192.168.4.118", "192.168.2.112", "192.168.2.109", "192.168.2.112", "192.168.2.105", "192.168.1.105", "192.168.5.122", "147.32.84.180", "147.32.84.170", "147.32.84.150", "147.32.84.140", "147.32.84.130", "147.32.84.160", "10.0.2.15", "192.168.106.141", "192.168.106.131", "172.16.253.130", "172.16.253.131", "172.16.253.129", "172.16.253.240", "74.78.117.238", "158.65.110.24", "192.168.3.35", "192.168.3.25", "192.168.3.65", "172.29.0.116", "172.29.0.109", "172.16.253.132", "192.168.248.165", "10.37.130.4"]
COLUMNS = [["ip.len", "frame.time_epoch", "tcp.len", "udp.len"], ["eth.dst", "tcp.dstport", "tcp.srcport", "udp.dstport", "udp.srcport", "ip.proto", "ip.flags", "frame.protocols", "tcp.flags"], ["ip.src", "ip.dst"], "FlowNo"]
CATEGORICAL_COLUMNS = [["eth.dst", "tcp.dstport", "tcp.srcport", "udp.dstport", "udp.srcport", "ip.proto", "ip.flags", "frame.protocols", "tcp.flags"]]
