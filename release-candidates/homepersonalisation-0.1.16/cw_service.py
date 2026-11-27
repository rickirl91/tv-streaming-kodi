import json
import xbmc
import xbmcvfs
from continue_watching_monitor import run

def rpc(method, params):
    result = json.loads(xbmc.executeJSONRPC(json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params})))
    if 'error' in result:
        raise RuntimeError('Kodi RPC failed')
    return result['result']

if __name__ == '__main__':
    run(xbmc, xbmcvfs, rpc)
