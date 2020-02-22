# stupidproxy
a stupid programmable reverse proxy. not increadibly fast.
the point isn't for this to be good, or fast. the point is for
it to be light weight, so we can improve on it later or use something better

## what it does
you can use the api to setup vhosts to redirect to, and then it will redirect those vhosts.

## example use
say for example you have a bunch of containers running and you want to dynamically
route various hostnames to containers. you can point a *.yoursite.org record to the
proxy server. you can use the api to setup <username>.yoursite.org as pointing to a
a container for the user, ang give them, for example, their own wordpress instance.
its highly suggested to setup a vhost for the apiserver like api.yoursite.org

## how it works
there is a proxy server written with raw werkzug, and then a flask api server.
they both share a sqlite database, so they need to have the same working directory.

## API
### web
- `GET /vhost/<vfrom>` get what host `<vfrom>` maps to
- `PUT /vhost/<vfrom>/<vto>` update or inster mapping from `<vfrom>` to `<vto>`
- `DELETE /vhost/<vfrom>` remove mapping fro `<vfrom>`
- `GET /vhost` list all vhost mappings
### python
- VHostClient
  + `__init__(dbname='hostmap.db')`
  + `get(vfrom)`
  + `put(vfrom, vto)`
  + `delete(vfrom)`
  + `list()` returns all mapings in form of [{vfrom, vto}]
  + `get_conn()` get connection to database
  + `get_cursor()`
  + `commit()`

## running it/local dev
- (optional) `virtualenv -p python3 env; source env/bin/activate` make a virtualenv if you want 
- `python3 stupidproxy.py` starts the proxy and creates the database
- `python3 stupidproxyapi.py` starts the apiserver
- (optional) `curl localhost:5001/vhost/api.yoursite.org/localhost:5001 -X PUT` create a vhost for the api

## deployment
idk use uwsgi or gunicorn or something and run the two aplications
