import os, urllib2, time, gzip, functools, datetime, ConfigParser
from flask import Flask, Response, after_this_request, request, make_response
from wsgiref.handlers import format_date_time
from email.utils import formatdate
from cStringIO import StringIO as IO
wraps = functools.wraps
app = Flask(__name__)

user_cache = [0, 0, '']

fd = open('ban.conf', 'r')
config = ConfigParser.ConfigParser()
config.readfp(fd)
fd.close()

conf_hostname = config.get('network', 'hostname')
conf_port = int(config.get('network', 'port'))

voat = config.get('main', 'voat')
voat = os.environ.get("VOAT", voat)

expires = int(config.get('main', 'expires'))
expires = os.environ.get("EXPIRES", expires)

counter = int(config.get('main', 'counter-cache'))
counter = os.environ.get("COUNTER", counter)

try:
    debug = bool(config.get('main', 'debug'))
except:
    debug = False
    
debug = bool(os.environ.get("DEBUG", debug))

def cache(expires=None, round_to_minute=False):
    """
    Add Flask cache response headers based on expires in seconds.

    If expires is None, caching will be disabled.
    Otherwise, caching headers are set to expire in now + expires seconds
    If round_to_minute is True, then it will always expire at the start of a minute (seconds = 0)

    Example usage:

    @app.route('/map')
    @cache(expires=60)
    def index():
      return render_template('index.html')

    """
    def cache_decorator(view):
        @wraps(view)
        def cache_func(*args, **kwargs):
            now = datetime.datetime.now()

            response = make_response(view(*args, **kwargs))
            response.headers['Last-Modified'] = format_date_time(time.mktime(now.timetuple()))

            if expires is None:
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
                response.headers['Expires'] = '-1'
            else:
                expires_time = now + datetime.timedelta(seconds=expires)

                if round_to_minute:
                    expires_time = expires_time.replace(second=0, microsecond=0)

                response.headers['Cache-Control'] = 'public'
                response.headers['Expires'] = format_date_time(time.mktime(expires_time.timetuple()))

            return response
        return cache_func
    return cache_decorator

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
    timestamp = int(now / counter)

    if user_cache[0] != timestamp:
        user_cache[0] = timestamp
        req = urllib2.Request("https://voat.co/v/" + voat + "/modlog/bannedusers", headers={ 'User-Agent': 'UNIX:the_kgb:0.157' })
        fd = urllib2.urlopen(req)

        for line in fd:
            if 'Total users banned' in line:
                num = int(line.split(':')[1])
                if num != user_cache[1]:
                    user_cache[1] = num
                    user_cache[2] = formatdate(timeval=now, localtime=False, usegmt=True)
                break

    return user_cache[1]

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

@app.route('/')
@gzipped
def main():
    return "FPH bans web app.<br><a href='/light/bans.svg'>Light counter</a><br><a href='/dark/bans.svg'>Dark counter</a>"

@app.route('/light/bans.svg')
@cache(expires=expires)
@gzipped

def light():
    resp = Response(getsvg_light(), mimetype='image/svg+xml')
    resp.headers['Last-Modified'] = user_cache[2]
    return resp

@app.route('/dark/bans.svg')
@cache(expires=expires)
@gzipped
def dark():
    resp = Response(getsvg_dark(), mimetype='image/svg+xml')
    resp.headers['Last-Modified'] = user_cache[2]
    return resp

if __name__ == "__main__":
    port = int(os.environ.get("PORT", conf_port))
    app.run(host=conf_hostname,port=port, debug=debug)
