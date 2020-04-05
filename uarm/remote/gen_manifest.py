import json
import os

from uarm.osc.uarm_osc_server import uarm_osc_server_gen_manifest


if __name__ == '__main__':
    file_name = 'swift_api_wrapper_osc.json'
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, file_name)
    manifest = uarm_osc_server_gen_manifest()
    manifest_json = json.dumps(manifest, indent=4)
    with open(file_path, 'w') as f:
        f.write(manifest_json)
