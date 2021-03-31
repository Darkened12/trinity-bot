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
