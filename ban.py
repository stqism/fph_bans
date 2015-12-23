import os, urllib2, time, gzip, functools
from flask import Flask, Response, after_this_request, request
from email.utils import formatdate
from cStringIO import StringIO as IO
app = Flask(__name__)

cache = [0, 0, '']

def gzipped(f):
    @functools.wraps(f)
    def view_func(*args, **kwargs):
        @after_this_request
        def zipper(response):
            accept_encoding = request.headers.get('Accept-Encoding', '')

            if 'gzip' not in accept_encoding.lower():
                return response

            response.direct_passthrough = False

            if (response.status_code < 200 or
                response.status_code >= 300 or
                'Content-Encoding' in response.headers):
                return response
            gzip_buffer = IO()
            gzip_file = gzip.GzipFile(mode='wb',
                                      fileobj=gzip_buffer)
            gzip_file.write(response.data)
            gzip_file.close()

            response.data = gzip_buffer.getvalue()
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Vary'] = 'Accept-Encoding'
            response.headers['Content-Length'] = len(response.data)

            return response

        return f(*args, **kwargs)

    return view_func

def getusers():
    now = time.time()
    timestamp = int(now / 100)

    if cache[0] != timestamp:
        cache[0] = timestamp
        req = urllib2.Request("https://voat.co/v/fatpeoplehate/modlog/bannedusers", headers={ 'User-Agent': 'UNIX:the_kgb:0.157' })
        fd = urllib2.urlopen(req)

        for line in fd:
            if 'Total users banned' in line:
                num = int(line.split(':')[1])
                if num != cache[1]:
                    cache[1] = num
                    cache[2] = formatdate(timeval=now, localtime=False, usegmt=True)
                break

    return cache[1]

def getsvg_light():
    data = """
<svg xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink" width="390" height="335">

<text x="55" y="150" font-family="Verdana" font-size="90">%s</text>
<text x="15" y="250" font-family="Verdana" font-size="90">BANS</text>
<text x="63" y="15" font-family="Verdana" font-size="12">This is an unpaid demo</text>
<text x="50" y="320" font-family="Verdana" font-size="12">Credit: /u/coup_de_shitlord</text>
</svg>
""" % (getusers())

    return data

def getsvg_dark():
    data = """
<svg xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink" width="390" height="335" style="fill:rgb(256,256,256)">

<text x="55" y="150" font-family="Verdana" font-size="90">%s</text>
<text x="15" y="250" font-family="Verdana" font-size="90">BANS</text>
<text x="63" y="15" font-family="Verdana" font-size="12">This is an unpaid demo</text>
<text x="50" y="320" font-family="Verdana" font-size="12">Credit: /u/coup_de_shitlord</text>
</svg>
""" % (getusers())

    return data

@app.route('/light/bans.svg')
@gzipped
def light():
    resp = Response(getsvg_light(), mimetype='image/svg+xml')
    resp.headers['Last-Modified'] = cache[2]
    return resp

@app.route('/dark/bans.svg')
@gzipped
def dark():
    resp = Response(getsvg_dark(), mimetype='image/svg+xml')
    resp.headers['Last-Modified'] = cache[2]
    return resp

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8008))
    app.run(host='0.0.0.0',port=port)
