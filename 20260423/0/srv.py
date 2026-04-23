import asyncio, root

async def echo(reader, writer):
	while data := await reader.readline():
		res = data.strip().decode()
		try:
			answer.root.sqroot(res)
		except Exception:
			answer = ''
	    writer.write(f"{answer}\n".encode())
	writer.close()
	await writer.wait_closed()
	
async def main():
	server = await asyncio.start_server(echo, '0.0.0.0', 1337)
	async with server:
		await server.serve_forever()

asyncio.run(main())
