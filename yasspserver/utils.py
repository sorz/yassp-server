from ssmanager import Server

def parse_servers(profiles_json):
    """Convert JSON-array profiles sent by web server
    into a tuple instance of Server.
    """
    return(Server(port=int(p['port']), password=p['passwd'],
                  method=p['method'], ota=p['ota']=='1')
           for p in profiles_json)

