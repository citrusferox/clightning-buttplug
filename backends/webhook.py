#!/usr/bin/env python3
import requests

class WebhookBackend:
    def __init__(self, 
                 invoice_url="http://localhost:8080/invoice/",
                 route_url=None
                 ):
        self.invoice_url = invoice_url
        self.route_url = route_url

    def notify(self, event):
        pass

    def on_route(self, fee_msat, **kwargs):
        if self.route_url is not None:
            requests.get(self.route_url)

    def on_payment(self, amount_msat, **kwargs):
        if self.invoice_url is not None:
            requests.get(self.invoice_url)

if __name__ == '__main__':
    backend = WebhookBackend()
    backend.on_payment(100e3)