#!/usr/bin/env python3.7
from buttplug.client import (ButtplugClientWebsocketConnector, ButtplugClient,
                             ButtplugClientDevice, ButtplugClientConnectorError)
from buttplug.core import ButtplugLogLevel
import asyncio

class SexToyBackend:
    def __init__(self, websocket="ws://127.0.0.1:12345", name="Lightning Plug"):
        self.ws = websocket
        self.name = name
        asyncio.run(self.vibrate(), debug=True)

    async def vibrate(self, intensity=0.5, duration=0.3):
        self.intensity = intensity
        self.duration = duration
        # create client
        client = ButtplugClient(self.name)
        # connect to websocket of the intiface
        connector = ButtplugClientWebsocketConnector(self.ws)
        # add event handler
        client.device_added_handler += self.device_added
        # asyncio
        # connect to device
        try:
            await client.connect(connector)
        except ButtplugClientConnectorError as e:
            print("Could not connect to server, exiting: {}".format(e.message))
            return

        # get logs
        await client.request_log(ButtplugLogLevel.debug)
        # search for devices
        await client.start_scanning()

        # wait
        task = asyncio.create_task(self.cancel_me())
        try:
            await task
        except asyncio.CancelledError:
            pass

        # ctrl-c -> stop
        await client.stop_scanning()
        # Now that we've done that, we just disconnect and we're done!
        await client.disconnect()

    # just sleep and wait for ctrl-c
    async def cancel_me(self):
        try:
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

    def device_added(self, emitter, dev: ButtplugClientDevice):
        asyncio.create_task(self.vibrate_task(dev))

    async def vibrate_task(self, dev: ButtplugClientDevice):
        # print("Device Added: {}".format(dev.name))
        # check we can vibrate
        if "VibrateCmd" in dev.allowed_messages.keys():
            # vibrate at 50% speed for 1 second
            await dev.send_vibrate_cmd(self.intensity)
            await asyncio.sleep(self.duration)
            await dev.send_stop_device_cmd()
        # check if it can move
        if "LinearCmd" in dev.allowed_messages.keys():
            # move to 90% in 1 second (1000ms).
            await dev.send_linear_cmd((int(self.duration*1e3), self.intensity))
            # wait 1s and move back
            await asyncio.sleep(self.duration)
            await dev.send_linear_cmd((int(self.duration*1e3), 0))

    def notify(self, intensity, duration):
        asyncio.run(self.vibrate(intensity, duration), debug=True)

    def on_route(self, fee_msat, **kwargs):
        self.notify(0.5, 0.3)

    def on_payment(self, amount_msat, **kwargs):
        self.notify(0.5, 1)

if __name__ == '__main__':
    dev = SexToyBackend()
    dev.on_route(100)
    dev.on_payment(1000)
