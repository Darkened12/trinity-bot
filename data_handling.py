import json
import aiofiles


async def open_file(file_name, mode='r'):
    async with aiofiles.open(file_name, mode=mode) as file:
        return await file.read()


async def write_file(file_name, data, mode='w'):
    if mode == 'a':
        async with aiofiles.open(file_name, mode='a') as file:
            return await file.writelines(data)
    async with aiofiles.open(file_name, mode=mode) as file:
        return await file.write(data)


async def load_json(file_name):
    async with aiofiles.open(file_name) as file:
        contents = await file.read()
        return json.loads(contents)


async def write_json(file_name, data):
    return await write_file(file_name, json.dumps(data, indent=4))
