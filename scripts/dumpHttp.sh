tcpdump -s 0 -A '(tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x504f5354)'