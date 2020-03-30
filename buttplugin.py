#!/usr/bin/env python3
from lightning import Plugin

# import notification backend
# here we use SayBackend - text-to-speach program
# like `say` or `espeak`
from backends.say import SayBackend
# PostBackend can make post requests to the server
# useful to notify donation server about new payment
from backends.post import PostBackend

plugin = Plugin()

# Create a backend with necessary init parameters
# in this case we use `espeak` process to notify us
backends = [
    PostBackend("http://localhost:8080/invoice/", "http://localhost:8080/route/"),
    SayBackend("espeak")
]

@plugin.method("buttplug")
def buttplug(plugin, method="payment", amount=1000):
    """Test your excitement when stacking sats.

    buttplug payment 1000 - feel like invoice for 1000 sat was paid;
    buttplug route 1 - feel like a payment was routed with 1 sat fee 
    """
    amount = float(amount)
    # craft events and call corresponding notifications
    if method=="payment":
        invoice_payment = {
            "label":"dummy",
            "preimage": "dummy",
            "msat": "%dmsat" % (amount*1e3)
        }
        on_payment(plugin, invoice_payment)
        return "Should feel like a %d satoshi invoice got paid" % amount
    elif method=="route":
        forward_event = {
            "status": "settled",
            "fee_msat": "%dmsat" % (amount*1e3)
        }
        on_forward(plugin, forward_event)
        return "Should feel like a payment with %d msat fee was routed" % (amount*1e3)
    return "Unsupported buttplug command"

@plugin.init()
def init(options, configuration, plugin, **kwargs):
    for backend in backends:
        backend.notify("Buttplug initialized")
    plugin.log("Plugin buttplug.py initialized")

@plugin.subscribe("forward_event")
def on_forward(plugin, forward_event, **kwargs):
    # check that routing is complete
    if forward_event.get("status") == "settled":
        # get the fee
        amount = int(forward_event.get("fee_msat").replace("msat",""))
        # TODO: get pattern and other vibro parameters
        # vibrate for routing
        for backend in backends:
            backend.on_forward(amount)

        plugin.log("Routed a payment with %d millisatoshi fee" % amount)
    else:
        plugin.log("Routing... Status: %r" % forward_event.get("status"))

@plugin.subscribe("invoice_payment")
def on_payment(plugin, invoice_payment, **kwargs):
    # get invoice amount
    amount = int(invoice_payment.get("msat").replace("msat",""))
    # TODO: get pattern and other vibro parameters
    # vibrate for payment
    for backend in backends:
        backend.on_payment(amount)
        plugin.log("backend: %r" % backend)

    plugin.log("Received invoice_payment event for label {}, preimage {},"
               " and amount of {}".format(invoice_payment.get("label"),
                                          invoice_payment.get("preimage"),
                                          invoice_payment.get("msat")))

if __name__ == '__main__':
    # adding buttplug parameters
    # TODO: good names...
    plugin.add_option('buttpattern', '419', 'Vibro pattern to use.')
    plugin.run()
