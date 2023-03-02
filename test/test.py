import socket
import time

def main():
    serv_address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print('takeoff')
    send_len = sock.sendto('t'.encode('utf-8'), serv_address)
    time.sleep(5)

    print('linetrace start')
    send_len = sock.sendto('1'.encode('utf-8'), serv_address)
    time.sleep(60)

    print('linetrace stop')
    send_len = sock.sendto('0'.encode('utf-8'), serv_address)
    time.sleep(5)

    print('landing')
    send_len = sock.sendto('l'.encode('utf-8'), serv_address)
    time.sleep(10)

if __name__ == '__main__':
    main()
