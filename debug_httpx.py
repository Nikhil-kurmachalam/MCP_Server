import httpx
import asyncio

URL = "https://mcp-server-32772794748.us-south1.run.app/sse"

async def test_connection(http2=True):
    print(f"\nScanning {URL} with http2={http2}...")
    try:
        async with httpx.AsyncClient(http2=http2, verify=False) as client:
            headers = {"Accept": "text/event-stream"}
            response = await client.get(URL, headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Protocol: {response.http_version}")
            print(f"Headers: {response.headers}")
    except Exception as e:
        print(f"Error: {e}")

async def main():
    await test_connection(http2=True)
    await test_connection(http2=False)

if __name__ == "__main__":
    asyncio.run(main())
