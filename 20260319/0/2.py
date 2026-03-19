import asyncio

comands = ["print ", "info host", "info port"]


async def handle(reader, writer):
    addr = writer.get_extra_info('pername')
    while line := await reader.readline():
        cmd = line.decode().strip()
        if cmd.startswith('print '):
            writer.write(f"{cmd[6:]}.\n".encode())
        elif cmd.startswith('info host'):
            writer.write(f"{addr[0]}\n".encode())


async def echo(reader, writer):
    while data := await reader.readline():
        writer.write(data.swapcase())
    writer.close()
    await writer.wait_closed()


async def main():
    server = await asyncio.start_server(echo, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()


asyncio.run(main())