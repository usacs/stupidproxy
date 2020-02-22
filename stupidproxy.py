from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response
import sqlite3
import requests

conn = sqlite3.connect('hostmap.db')

def wsgiapp(environ, start_response):
    req = Request(environ)
    c = conn.cursor()
    q_data = (req.host,)
    c.execute('select vto from vhosts where vfrom=?', q_data)
    mapped_host = c.fetchone()[0]
    print(mapped_host)
    print({
        'method': req.method,
        'headers': req.headers,
        'body': req.get_data(),
        'path': req.path + '?' + req.query_string.decode('utf-8'),
        'host': req.host,
    })
    full_url = 'http://' + mapped_host + req.path + '?' + req.query_string.decode('utf-8')
    print(full_url)
    # TODO x-forwarded-for
    upstream_req = requests.Request(req.method, full_url, data=req.get_data(),
                                    headers=req.headers)
    session = requests.Session()
    upstream_res = session.send(upstream_req.prepare())
    print(dir(upstream_res))
    print(upstream_res.headers)
    res = Response(upstream_res.text, status=upstream_res.status_code,
                   headers=list(upstream_res.headers.items()))
    return res(environ, start_response)

def create_table():
    c = conn.cursor()
    c.execute('create table if not exists vhosts (vfrom text, vto text)')
    c.execute('create unique index idx_vhosts_vfrom on vhosts (vfrom)')
    conn.commit()

if __name__ == '__main__':
    create_table()
    run_simple('127.0.0.1', 5000, wsgiapp, use_debugger=False, use_reloader=False)
    conn.close()
