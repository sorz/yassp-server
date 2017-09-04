# yassp-server

yassp-server was **a part of** an internal closed source project called Yet Another ShadowSocks Panel (YaSSP). Like [ss-panel](https://github.com/orvice/ss-panel/), YaSSP was a full-functional Shadowsocks panel with user management, accounting, sales, et al. However, this project has been dead.

```
  +---------+            +---------------+-------------+
  |         |    HTTP    |               |             |
  |  YaSSP  | <--------> | yassp-server <-> SS servers |
  |         |            |  (this repo)  |             |
  +---------+            +---------------+-------------+
single control              may have multiple instances
    server
```

yassp-server is a daemon progrom running on server where SS servers run. It synchronizes user configurations and traffics with YaSSP, and is responsible for run/stop/restart SS servers.

Since the original project has been **dead**, this repo is **unlikely to be maintained**.

## Features
* Support both SS-Python and SS-libev ports (see [ssmanager](https://github.com/sorz/ssmanager/))
* Pull SS configs via HTTP API
* Also an optional push API for update SS configs
* Configurable hostname & pre-shared key pair for multiple servers
* Accounting: push traffic usage via HTTP API
* Traffic usage won't lost on temporary network/server issues and normal shutdown/restart


## API

Based on JSON & HTTP. Variables are configured on `config.cfg`.


### Profiles
A JSON list of SS configs. For example,
```json
[{"port": 8001, "method": "aes-256-gcm", "password": "password"},
 {"port": 8002, "method": "chacha20-ietf-poly1305", "password": "test123"}]
```
All arguments are passed to `ssmanager` and then to SS server eventually, see docs of SS for available args.

### Pull configs
yassp-server will pull SS configs from `{yassp url}`.

* HTTP `GET` `{yassp url}/services/`
* With HTTP basic auth `{yassp hostname}:{yassp psk}`
* Return `200 OK`, `Profiles` as body (see previous section), or 
* `304 Not Modified` if configs not change since last pull *.

\* Both `last_modified` and `etag` headers are supported.

### Push configs

If enabled, a simple HTTP server will run on `{push bind address}:{push bind port}`.

To push configs, send a `POST` to `/instances?token={push token}`,
with `Profiles` as body. `204 No Content` will returned.

### Traffic stats

Traffic stats will be `PUSH`ed to `{yassp url}/traffics/`. Body is a JSON dict of `{port number: traffic in bytes since last upload}`, Auth header is the same as pull configs'.

