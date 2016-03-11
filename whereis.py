"""
Where is all the Internets
"""

from kochira.service import Service
from operator import itemgetter
from ftplib import FTP
import struct
import socket

service = Service(__name__, __doc__)

def quadToLong(ip):
    return struct.unpack('!L',socket.inet_aton(ip))[0]

file_content = []
def add_to_file_content(line):
    file_content.append(line)

ftp = FTP('ftp.net.berkeley.edu')
ftp.login()
ftp.cwd('pub')
ftp.retrlines('RETR networks.local', add_to_file_content)
subnet_list = [ line.strip().split("\t") for line in
        [x for x in file_content if '#' not in x[0]] ]

# parse into ([ip, prefixlength], desc)
subnets = [ (x[1].split("/"), x[2][2:]) for x in
        [x for x in subnet_list if len(x) == 3] ]

# convert to (long_ip, subnet_mask, desc)
longsubnets = [ (quadToLong(x[0]), int(x[1]), y) for x, y in subnets ]
longsubnets.sort(key=itemgetter(1), reverse=True)
longsubnets = [ (x, (0xFFFFFFFF << (32 - int(y))) & 0xFFFFFFFF, z) for x, y, z in longsubnets ]
longsubnets = [ (x & y, y, z) for x, y, z in longsubnets ]

def findsubnet(ip):
    ip = quadToLong(socket.gethostbyname(ip))
    for x, y, z in longsubnets:
        if (x == (ip & y)):
            return z
    
@service.command(r"!(wi|whereis) (?P<ip>.*)$")
def get_subnet(ctx, ip):
    """
    Get subnet info for IP address
    """
    try:
        ctx.message("{0} is {1}".format(ip, findsubnet(ip)))
    except Exception as e:
        ctx.message("Python stinx: {0}".format(e))
