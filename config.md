Config file:
===

The default config file looks like such:

```
[network]
hostname=0.0.0.0
port=8008

[main]
voat=fatpeoplehate
expires=300
counter-cache=100
```

* hostname: the hostname/ip to bind to
* port: the port to listen on
* voat: the channel to read bans from
* expires: the seconds to cache in browsers for
* counter-cache: What to divide a unix timestamp by to get a range to cache API calls
* debug: Set to debug, this is optional

Settings on Heroku:
===
If you use Heroku you can set most of the settings using config vars
In your apps settings click reveal config vars and add/edit keys as needed

* VOAT: voat
* EXPIRES: expires
* COUNTER: counter-cache
* DEBUG: debug
