#!/usr/bin/python3


import atexit
import liblo
import socket
from   subprocess import Popen, DEVNULL
import sys
import time


def get_free_port():
    s = socket.socket()
    s.bind(("", 0))
    return s.getsockname()[1]


def run(*args, **kwargs):
    #stdin  = kwargs.get('stdin',  DEVNULL)
    #stdout = kwargs.get('stdout', DEVNULL)
    #stderr = kwargs.get('stderr', DEVNULL)
    subprocess = Popen(args)
        #args, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
    atexit.register(lambda: subprocess.kill())
    return subprocess


name  = 'HUMPTY' if len(sys.argv) <= 1 else 'DUMPTY'
start = None


def t():
    return int(time.time() * 1000000)


def log(msg, tick=None):
    ts = (tick or t()) - start
    print('[ {0} ] {1}  {2}'.format(name, ts, msg))


if __name__ == '__main__':

    if name == 'HUMPTY':
        start   = t()
        log('Starting first process.')
        port    = get_free_port()
        dumpty  = run('./latency.py', str(port), str(start))
        address = liblo.Address(port)
        log('Started first process.')

        while True:
            tick = t() - start
            log('Sending ping {0}'.format(tick))
            liblo.send(address, '/ping', tick)
            time.sleep(1)

    elif name == 'DUMPTY':
        start   = int(sys.argv[2])
        log('Starting second process.')
        port       = int(sys.argv[1])
        server     = liblo.Server(port)
        latency    = 0
        lat_n      = 0
        deviation  = 0
        dev_n      = 0

        def on_ping(path, args):
            global latency, lat_n, deviation, dev_n

            ping        = args[0]
            tick        = t() - start
            td          = tick - ping
            latency    += td
            lat_n      += 1
            avglat      = latency / lat_n
            dev         = avglat - td
            deviation  += abs(dev)
            dev_n      += 1
            avgdev      = deviation / dev_n

            log('Pinged {0}us, avg {1}us, dev {2}us, avgdev {3}us'.format(
                td, round(avglat, 2), round(dev, 2), round(avgdev, 2)))

        server.add_method('/ping', 'h', on_ping)

        log('Started second process on port {0}.'.format(port))

        while True:
            server.recv()
