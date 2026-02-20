import asyncio
import edge_tts

async def main():
    voices = await edge_tts.list_voices()
    for v in voices:
        if 'vi-VN' in v['ShortName']:
            print(f"Name: {v['ShortName']}, Gender: {v['Gender']}")

asyncio.run(main())
