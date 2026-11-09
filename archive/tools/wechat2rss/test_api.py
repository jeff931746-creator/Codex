#!/usr/bin/env python3
"""Read-only article API checks; configure WX_API_KEY in the environment."""
import json
import os
import urllib.parse
import urllib.request


def main() -> int:
    key = os.environ.get('WX_API_KEY')
    if not key:
        raise SystemExit('Set WX_API_KEY before running this script.')
    base = os.environ.get('WX_BASE_URL', 'https://down.mptext.top').rstrip('/')
    for endpoint in ('/api/public/v1/authkey', *('/api/public/v1/account?' + urllib.parse.urlencode({'keyword': name}) for name in ('GameLook', '出海独联体'))):
        request = urllib.request.Request(base + endpoint, headers={'X-Auth-Key': key})
        with urllib.request.urlopen(request, timeout=30) as response:
            print(json.dumps(json.load(response), ensure_ascii=False, indent=2)[:1000])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
