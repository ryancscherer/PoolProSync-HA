<p align="center">
  <img src="assets/icon@2x.png" alt="Pool Pro Sync HA" width="160">
</p>

<h1 align="center">Pool Pro Sync HA</h1>

<p align="center">
  <a href="https://github.com/hacs/integration"><img alt="HACS Custom" src="https://img.shields.io/badge/HACS-Custom-41BDF5.svg"></a>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-blue.svg"></a>
  <img alt="Version" src="https://img.shields.io/badge/version-0.2.1-informational">
</p>

Pool Pro Sync HA brings your PoolPro Sync salt chlorinator into Home Assistant. You get live readings from your pool controller and a few ways to control it, all inside Home Assistant instead of only in the PoolPro Sync phone app.

PoolPro Sync does not publish an official API. This integration was built by capturing and studying the real traffic the official app sends, then recreating that behaviour inside a Home Assistant custom integration. That also means it could break if PoolPro Sync changes something on their end, though nothing about this has changed so far.

## What you get

Once it is set up, Home Assistant creates one device for your pool controller with the following entities.

Sensors:

* Water temperature
* Controller temperature
* Salt level
* Cell status
* Chlorine output
* Fault code

Controls:

* Power mode, a dropdown for switching the unit between auto, on and off
* Work mode, a dropdown for the special modes such as spa, winter, boost, backwash and salt test
* pH pump, a simple switch to turn the dosing pump on or off

All of these update automatically while Home Assistant is running. You do not need to press refresh or poll anything yourself.

Because everything shows up as normal Home Assistant entities, you can use them exactly like any other device. Add them to a dashboard, graph the water temperature over time, get a notification when the fault code changes, or build an automation that turns on a light when the pump starts running.

## Before you start

You will need the device ID for your pool controller. Open the PoolPro Sync app, go to your device's details screen, and look for an ID that looks like a string of letters and numbers, for example AABBCC112233. Write it down or copy it somewhere, you will need to paste it in during setup.

Treat that device ID a bit like a password. Do not post it publicly in forum threads, screenshots or support tickets. The way PoolPro Sync's backend works, anyone who has your device ID can read and change your pool controller's settings, so it is worth keeping private.

## Installing through HACS

1. Open HACS inside Home Assistant.
2. Go to the three dot menu in the top right and choose Custom repositories.
3. Paste in this address: https://github.com/ryancscherer/PoolProSync-HA
4. Set the category to Integration and add it.
5. Find "Pool Pro Sync HA" in the HACS integration list and install it.
6. Restart Home Assistant so it picks up the new integration.

## Setting it up

1. Go to Settings, then Devices and Services.
2. Click Add Integration and search for PoolPro Sync.
3. Enter the device ID you found earlier.
4. Click submit.

That is it. You do not need a username or password for your PoolPro Sync account. The app itself does not ask for one either when talking to its backend, it only needs the device ID to know which pool controller to talk to. Home Assistant also works out which product you have on its own, so there is nothing else to fill in.

Within a few seconds your sensors should start showing real values and the controls should start reflecting the current state of your pool equipment.

## Using it day to day

Once the device and its entities exist, there is nothing special to learn. A few ideas for things people commonly do with it:

* Add a simple card to your dashboard showing water temperature and salt level at a glance.
* Set up an automation that notifies you if the fault code changes away from zero.
* Track water temperature history over the season using Home Assistant's built in history and statistics graphs.
* Turn the pump or pH dosing on a schedule using Home Assistant automations instead of the timers built into the controller.

## A few things worth knowing

This integration has been tested against a SLIMLINE series salt chlorinator. Other PoolPro Sync product lines likely use the same underlying system, since it is a fairly generic platform, but they have not been tested personally. If you try it on a different model and something does not work right, please open an issue and include what you are seeing.

Three extra properties that the device advertises, chlorine production, copper level and wifi signal, are not shown as entities. In testing, the real device never actually sent values for these, no matter what was tried, so they would only ever sit there showing unknown. Rather than clutter your entity list with sensors that never update, they were left out.

Sometimes the pool controller is a little slow to answer a request for a full refresh of its status, and occasionally it does not answer at all in time. This is a limitation on the controller or its gateway, not something wrong with the integration, and it recovers on its own on the next refresh.

## Getting help or contributing

If something is not working, open an issue on GitHub and describe what you are seeing, including anything from Home Assistant's own log that mentions poolpro_sync.

If you own a different PoolPro Sync product and want to help add support for it, the most useful thing you can provide is a packet capture of the app talking to the device, ideally with the traffic decrypted so the actual requests and responses are visible. That is how this integration itself was originally built.

## License

This project is released under the MIT license. See the LICENSE file for the full text.

## Disclaimer

This is an independent, community built integration. It is not made by, affiliated with, or endorsed by PoolPro Sync. It relies on behaviour of an unofficial, undocumented API, which could change at any time. The icon used in this project is an original design and is not PoolPro Sync's own artwork.

## About the developer

This project was built and is maintained by Ryan Scherer of Scherer Co. You can find more of his work at https://schererco.com/.
