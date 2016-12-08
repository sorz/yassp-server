from ssmanager import Server


ss_bind_address = '0.0.0.0'

def parse_servers(profiles_json):
    return (Server(host=ss_bind_address, **p) for p in profiles_json)

