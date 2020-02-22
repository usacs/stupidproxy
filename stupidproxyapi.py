from flask import Flask, make_response, jsonify
import sqlite3
import atexit

conn = None
app = Flask(__name__)

class VHostClient:
    def __init__(self, dbname='hostmap.db', max_per_user=3):
        self.dbname = dbname
        self.max_per_user = max_per_user
        self.conn = None

    def get_conn(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.dbname)
        return self.conn

    def get_cursor(self, *args, **kwargs):
        return self.get_conn().cursor(*args, **kwargs)

    def commit(self, *args, **kwargs):
        return self.get_conn().commit(*args, **kwargs)

    def get(self, vfrom):
        c = self.get_cursor()
        q_data = (vfrom,)
        c.execute('select vto from vhosts where vfrom=?', q_data)
        res = c.fetchone()
        if res:
            return res[0]
        return None

    def put(self, vfrom, vto):
        c = self.get_cursor()
        q_data = (vfrom, vto)
        c.execute('insert or replace into vhosts values (?, ?)', q_data)
        self.commit()

    def delete(self, vfrom):
        c = self.get_cursor()
        q_data = (vfrom,)
        c.execute('delete from vhosts where vfrom=?', q_data)
        self.commit()

    def list(self, user=None):
        # todo implement users
        c = self.get_cursor()
        c.execute('select * from vhosts')
        rows = c.fetchall()
        result = []
        for row in rows:
            result.append({
                'vfrom': row[0],
                'vto': row[1]
            })
        return result

    def close(self, *args, **kwargs):
        res = self.get_conn().close(*args, **kwargs)
        self.conn = None
        return res

client = None

@app.route('/vhost/<vfrom>', methods=['GET'])
def getvhost(vfrom):
    try:
        res = client.get(vfrom)
        if res:
            return res
        return 'no vhost', 404
    except Exception as e:
        print(e)
        return 'unknown error', 500

@app.route('/vhost/<vfrom>/<vto>', methods=['PUT'])
def putvhost(vfrom, vto):
    try:
        client.put(vfrom, vto)
        return vto
    except Exception as e:
        print(e)
        return 'unknown error', 500

@app.route('/vhost/<vfrom>', methods=['DELETE'])
def deletevhost(vfrom):
    try:
        client.delete(vfrom)
        return 'removed'
    except Exception as e:
        print(e)
        return 'unknown error', 500

@app.route('/vhost', methods=['GET'])
def listvhosts():
    try:
        return jsonify(client.list())
    except Exception as e:
        print(e)
        return 'unknown error', 500


if __name__ == '__main__':
    client = VHostClient()
    atexit.register(client.close)
    app.run(port=5001)
