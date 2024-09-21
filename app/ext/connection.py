import aiohttp


async def get_request(endpoint, credentials=None, mode='text'):
    if credentials is None:
        credentials = {}
    async with aiohttp.ClientSession(headers={'Connection': 'keep-alive'}) as session:
        async with session.get(endpoint, params=credentials, timeout=7, allow_redirects=True) as resp:
            if mode == 'text':
                return await resp.text()
            elif mode == 'json':
                return await resp.json()
            else:
                return await resp.read()


async def post_request(endpoint, data, credentials=None, mode='json', timeout=7):
    if credentials is None:
        credentials = {}

    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, params=credentials, data=data, timeout=timeout) as resp:
            if mode == 'text':
                return await resp.text()
            elif mode == 'json':
                return await resp.json()
            else:
                return await resp.read()


async def is_url_ok(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return resp.status == 200
    except aiohttp.ClientError:
        pass
    return False
