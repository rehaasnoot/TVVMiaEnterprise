import os
import sys
import json
import threading
import time
from tvvconfig import TVVConfigAgent
from tvvlogger import TVVLogger
import requests
from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager, jwt_required, get_jwt_identity,
    create_access_token, create_refresh_token,
    jwt_refresh_token_required, get_raw_jwt
)

BREG_ENV="venv/lib/python2.7/site-packages"
sys.path.append(BREG_ENV) 
AGENT_NAME = 'tvvblagent'
AGENT_FORMAL_NAME = 'TVV_Blagent'

REGISTRY_FORMAL_NAME = 'TVV_Blagent_Registry'
BREG_NAME = 'tvvblagent_registry'
BREG_ROUTE_ROOT = '/' + BREG_NAME
BREG_ROUTE_LOGIN = BREG_ROUTE_ROOT + '/login'
BREG_ROUTE_REFRESH = BREG_ROUTE_ROOT + '/refresh'
BREG_ROUTE_PING = BREG_ROUTE_ROOT + '/ping'
BREG_ROUTE_LOGOUT = BREG_ROUTE_ROOT + '/logout'
BREG_ROUTE_QUIT = BREG_ROUTE_ROOT + '/quit'
BREG_ROUTE_LISTING = BREG_ROUTE_ROOT + '/listing'
BREG_ROUTE_LOOKUP = BREG_ROUTE_ROOT + '/lookup'
BREG_ROUTE_REGISTER = BREG_ROUTE_ROOT + '/register/<id>/<host>/<port>'
BREG_ROUTE_DEREGISTER = BREG_ROUTE_ROOT + '/deregister/<id>/<host>/<port>'
BREG_REGISTER_RETRY = 10.1

config = TVVConfigAgent()
DEBUG = True
if 'False' == config.get(REGISTRY_FORMAL_NAME, "DEBUG"):
    DEBUG = False
LOG = TVVLogger(REGISTRY_FORMAL_NAME, debug=DEBUG)

SECRET_KEY = config.get(AGENT_FORMAL_NAME, 'SECRET_KEY')
AGENT_HOST = config.get(AGENT_FORMAL_NAME, "HOST")
AGENT_PORT = config.get(AGENT_FORMAL_NAME, "PORT")
AGENT_USERNAME=config.get(AGENT_FORMAL_NAME, "USERNAME")
AGENT_PASSWORD=config.get(AGENT_FORMAL_NAME, "PASSWORD")
REGISTRY_HOST=config.get(REGISTRY_FORMAL_NAME, "HOST")
REGISTRY_PORT=config.get(REGISTRY_FORMAL_NAME, "PORT")
REGISTRY_USERNAME=config.get(REGISTRY_FORMAL_NAME, "USERNAME")
REGISTRY_PASSWORD=config.get(REGISTRY_FORMAL_NAME, "PASSWORD")
H = "http://{}:{}".format(REGISTRY_HOST, REGISTRY_PORT)
GET = "GET"
POST = "POST"
PUT = "PUT"
DELETE = "DELETE"
UPDATE = "UPDATE"
M_G = [GET]
M_P = [POST]
M_p = [PUT]
M_D = [DELETE]
M_GP = [GET, POST]

BREG_STATUS = None

class JSONify():
    def toJSON(self):
        if isinstance(self, list):
            return jsonify(self)
        if isinstance(self, tuple):
            return jsonify(self)
#        if isinstance(self, BREGS):
#            return jsonify(self.registered_blagents)
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class endpoint():
    name = None
    scheme = None
    hostname = None
    port = None
    def __init__(self, url=None):
        if None != url:
            from urllib.parse import urlparse
            up = urlparse(url)
            self.name = url
            self.scheme = up.scheme
            self.hostname = up.hostname
            self.port = up.port

class RET(JSONify): # Return codes
    code = None
    desc = None
    def __init__(self, code, desc):
        self.code = code
        self.desc = desc
    def __getitem__(self,index):
        return self.code
    def __setitem__(self,index,value):
        self.code = value
    def response(self):
        return self.toJSON(), self.code

RETURNS = [ RET(201, "Already registered"), RET(405, "None Available"), RET(200, "OK"), RET(418, "I'm a terminating...") ]
   
class BREG(JSONify):
    id = None
    scheme = "http"
    host = None
    port = None
    avail = True
    access_token = None
    refresh_token = None
    GET = 'GET'
    POST = 'POST'
    AGENT_API_NAME = 'tvvblagent'
    def __init__(self, id, host, port):
        self.id = id
        self.host = host
        self.port = port
        self.avail = True
    def getId(self):
        return self.id
    def setId(self, id):
        self.id = id
        return self.id
    def getHost(self):
        return self.host
    def getPort(self):
        return self.port
    def getAvail(self):
        return self.avail
    def response(self):
        return self.toJSON(), RETURNS[2][0]
    def regURL(self, function_name):
        return '{}://{}:{}/{}/{}'.format(self.scheme, self.host, self.port, self.AGENT_API_NAME, function_name)
    def login(self):
        basicCredentials = (REGISTRY_USERNAME, REGISTRY_PASSWORD) 
        # Send HTTP GET request to server and attempt to receive a response
        res = None
        status_code = None
        while res == None and status_code != 200:
            res = requests.post(self.regURL('login'), auth=basicCredentials)
            status_code = res.status_code
            time.sleep(2)
        res_json = json.loads(res.text)
        self.access_token = res_json['access_token']
        self.refresh_token = res_json['refresh_token']
        return res
    def request(self, request_type, function_name):
        if None == self.access_token:
            lres = self.login()
            while None == lres and lres.status_code != 200:
                lres = self.login()
                time.sleep(4)
        # Send HTTP GET request to server and attempt to receive a response
#        authCredentials = {'access-token': self.ACCESS_TOKEN, 'refresh-token': self.REFRESH_TOKEN}
        authCredentials = {'Authorization' : 'Bearer ' + self.access_token }
        resp = requests.request(method=request_type, url=self.regURL(function_name), headers=authCredentials)
        return resp
    def ping(self):
        resp = self.request(self.GET, 'ping')
        if resp.status_code == 200:
            self.avail = True
        else:
            self.avail = False
        return self.avail
    def available(self):
        resp = self.request(self.GET, 'available')
        if resp.status_code == 200:
            self.avail = False
        else:
            self.avail = True
        return self.avail
    def agentid(self):
        #req_url = 'http://{}:{}/{}/agentid'.format(self.host, self.port, AGENT_NAME)
        resp = self.request(self.GET, 'agentid')
        if resp.status_code == 200:
            resp_json = resp.json()
            self.setId(resp_json["id"])
            self.avail = True
#        else:
#            self.avail = False
        return self.avail
    def down(self):
        #req_url = 'http://{}:{}/{}/quit'.format(self.host, self.port, AGENT_NAME)
        self.avail = True
        resp = self.request(self.GET, 'quit')
        if resp.status_code == 200:
        # This means something went wrong.
        #raise ApiError('GET /tasks/ {}'.format(resp.status_code))
            self.avail = False
        return self.avail

class BREGS(JSONify):
    registered_blagents = None
    def __init__(self):
        self.registered_blagents = []
    def __getitem__(self,index):
        return self.registered_blagents[index]
    def __setitem__(self,index,value):
        self.registered_blagents[index] = value
    def append(self, breg):
        self.registered_blagents.append(breg)
    def size(self):
        if None == self.registered_blagents:
            return 0
        return self.registered_blagents.__len__()
    def getBregs(self):
        return self.registered_blagents
    def remove(self, i):
        del self.registered_blagents[i]
    def shutdown(self):
        for b in self.registered_blagents:
            b.down()
    def response(self):
        return self.toJSON(), RETURNS[2][0]

global BREG_LIST
BREG_LIST = BREGS()

def apiUsage():
    api_docs = { "BlBREG Registry Api": {
        "/" : "docs",
        H + BREG_ROUTE_PING : "Is alive?",
        H + BREG_ROUTE_LOGIN : "Basic authentication + return JWT",
        H + BREG_ROUTE_REFRESH : "Refresh api access credentials + return JWT",
        H + BREG_ROUTE_LOGOUT: "Revoke user access",
        H + BREG_ROUTE_LOOKUP : "Returns 1st available registered Blender Agent",
        H + BREG_ROUTE_LISTING : "Returns all registered Blender Agents",
        H + BREG_ROUTE_REGISTER : "Register host & port as a blender BREG",
        H + BREG_ROUTE_DEREGISTER : "De-Register host & port as a blender BREG",
        H + BREG_ROUTE_QUIT : "Quit",
        }
    }
    return api_docs

app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
# Enable blacklisting and specify what kind of tokens to check
# against the blacklist
app.config['JWT_SECRET_KEY'] = SECRET_KEY
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
jwt = JWTManager(app)

# A storage engine to save revoked tokens. In production if
# speed is the primary concern, redis is a good bet. If data
# persistence is more important for you, postgres is another
# great option. In this example, we will be using an in memory
# store, just to show you how this might work. For more
# complete examples, check out these:
# https://github.com/vimalloc/flask-jwt-extended/blob/master/examples/redis_blacklist.py
# https://github.com/vimalloc/flask-jwt-extended/tree/master/examples/database_blacklist
blacklist = set()

# For this example, we are just checking if the tokens jti
# (unique identifier) is in the blacklist set. This could
# be made more complex, for example storing all tokens
# into the blacklist with a revoked status when created,
# and returning the revoked status in this call. This
# would allow you to have a list of all created tokens,
# and to consider tokens that aren't in the blacklist
# (aka tokens you didn't create) as revoked. These are
# just two options, and this can be tailored to whatever
# your application needs.
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist

@app.route("/")
@jwt_required
def BREGRoot():
    return jsonify(apiUsage()), 200

# Standard login endpoint
@app.route(BREG_ROUTE_LOGIN, methods=M_P)
def BREGLogin():
    username = request.authorization['username']
    password = request.authorization['password']
    if username != AGENT_USERNAME or password != AGENT_PASSWORD:
        return jsonify({"msg": "Bad username or password"}), 401
    ret = {
        'access_token': create_access_token(identity=username),
        'refresh_token': create_refresh_token(identity=username)
    }
    return jsonify(ret), 200

# Standard refresh endpoint. A blacklisted refresh token
# will not be able to access this endpoint
@app.route(BREG_ROUTE_REFRESH, methods=M_P)
@jwt_refresh_token_required
def BREGRefresh():
    current_user = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=current_user)
    }
    return jsonify(ret), 200

@app.route('/logout', methods=['DELETE'])
@jwt_required
def BREGLogout():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return jsonify({"msg": "Successfully logged out"}), 200

# Endpoint for revoking the current users refresh token
@app.route('/logout2', methods=['DELETE'])
@jwt_refresh_token_required
def logout2():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return jsonify({"msg": "Successfully logged out"}), 200

# This will now prevent users with blacklisted tokens from
# accessing this endpoint
@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    return jsonify({'hello': 'world'})

@app.route(BREG_ROUTE_PING, methods=M_GP)
def BREGPing():
    return RETURNS[2].response()

@app.route(BREG_ROUTE_LOOKUP, methods=M_G)
@jwt_required
def BREGLookup():
    if None == BREG_LIST:
        rc = RETURNS[1]
        return rc.response()
    for b in BREG_LIST.getBregs():
        if not b.agentid():
            b.ping()
        if b.avail:
            return b.response()
    rc = RETURNS[1]
    return rc.response()
    
@app.route(BREG_ROUTE_LISTING, methods=M_G)
@jwt_required
def BREGListing():
    if None == BREG_LIST:
        rc = RETURNS[1]
        return rc.repsonse()
    return BREG_LIST.response()
    
@app.route(BREG_ROUTE_REGISTER, methods=M_P)
@jwt_required
def BREGRegister(id, host, port):
    if BREG_LIST.size() > 0:
        for b in BREG_LIST.getBregs():
            if host == b.getHost() and port == b.getPort():
                if id != b.id:
                    b.id = id
                rc = RETURNS[0]
                return rc.response()
    nb = BREG(id, host, port)
    nb.avail = True
    BREG_LIST.append(nb)
    return nb.response()
     
@app.route(BREG_ROUTE_DEREGISTER, methods=M_P)
@jwt_required
def BREGDeRegister(id, host, port):
    r = None
    i = 0
    for b in BREG_LIST.getBregs():
        if host == b.host:
            if port == b.port:
                if id == b.id:
                    r = i
                    break
        i += 1
    if None != r:
        BREG_LIST.remove(r)
    return RETURNS[2].response() #RETS[2].toJSON()

@app.route(BREG_ROUTE_QUIT)
@jwt_required
def BREGTerminate():
    BREG_LIST.shutdown()
    shutdown_server()
    return RETURNS[3].response() #RETS[3].toJSON()

def shutdown_server():
    BREG_STATUS = 'terminating'
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

def reregister():
    while BREG_STATUS != 'terminating':
        time.sleep(BREG_REGISTER_RETRY)
        LOG.log("testing blagents...")
        if None != BREG_LIST:
            i = 0
            for b in BREG_LIST.getBregs():
                if not b.agentid():
                    del BREG_LIST[i]
                i += 1

def main():
    t1 = threading.Thread(target=reregister)
    t1.start()
    BREG_STATUS = 'running'
    app.run(host=REGISTRY_HOST, port=REGISTRY_PORT)

if __name__ == "__main__":
    main()

