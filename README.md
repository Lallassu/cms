# Control My Spa

This is a simple integration that talks to controlmyspa.com and extracts the information for your spa,
such as temperature, pump state, light state etc.

**Note**: It is readonly and you cannot use this to control your spa. Mainly because it's not possible via
their website dashboard.

I created this in order to integrate with my WiFi enabled spa, which doesn't seem to be supported by the 
other integrations available in Home Assistant. So this integration should work with any spa that supports
the Control My Spa service.

Disclaimer: It might fail to work if you have multiple spas connected to your account, as I only have one spa and the
ID extraction might be different. Pull requests are welcome!

## Requirements

An account for https://controlmyspa.com/

## Installation

1. Clone this repo `git clone https://github.com/lallassu/cms` into your `custom_components` dir your Home Assistant installation.
2. Reload/restart Home Assistant
3. click "Add integartion" and search for "Control My Spa"
4. Login using the credentials for your CMS account.


