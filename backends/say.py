#!/usr/bin/env python3
import subprocess

class SayBackend:
    def __init__(self, process):
        self.process = process

    def notify(self, event):
        subprocess.run([self.process, event])

    def on_route(self, fee_msat, **kwargs):
        self.notify("Collected %d millisatoshi fee" % fee_msat)

    def on_payment(self, amount_msat, **kwargs):
        self.notify("Received payment of %d millisatoshi" % amount_msat)

if __name__ == '__main__':
    backend = SayBackend("espeak")
    backend.notify("received 100 satoshi")