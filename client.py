import json
from unittest import result
from aiohttp import ClientSession
from asyncio import run
from pprint import pprint

async def main():
    async with ClientSession() as session:
        # # POST
        # response = await session.post(
        #     url='http://127.0.0.1:8080/adverts/',
        #     json={
        #         'header': 'some_header1',
        #         'description': 'some description1',
        #         'owner': 'somebody1',
        #         },
        #     )
        # result = await response.text()
        # pprint(result)

        # # GET
        # response = await session.get(url='http://127.0.0.1:8080/adverts/1')
        # result = await response.text()
        # pprint(result)

        # # PATCH
        # response = await session.patch(
        #     url='http://127.0.0.1:8080/adverts/1',
        #     json={'header': 'another_header1'},
        #     )
        # result = await response.text()
        # pprint(result)

        # # DELETE
        # response = await session.delete(url='http://127.0.0.1:8080/adverts/1')
        # result = await response.text()
        # pprint(result)

        # # GET TO CHECK
        # response = await session.get(url='http://127.0.0.1:8080/adverts/1')
        # result = await response.text()
        # pprint(result)

run(main())