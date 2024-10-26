# home/consumers.py
import json
import asyncio
import aiohttp
from channels.generic.websocket import AsyncWebsocketConsumer

class BinanceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()  # 接受 WebSocket 連接
        self.keep_running = True
        self.binance_task = asyncio.create_task(self.start_binance_websocket())  # 啟動 Binance WebSocket 的任務

    async def disconnect(self, close_code):
        self.keep_running = False
        if self.binance_task:
            self.binance_task.cancel()  # 取消 Binance WebSocket 任務
        print(f"WebSocket 已斷開：{close_code}")

    async def receive(self, text_data):
        await self.send(text_data="服務器已收到您的消息：{}".format(text_data))

    async def start_binance_websocket(self):
        uri = "wss://stream.binance.com:9443/ws/btcusdt@trade"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(uri) as websocket:
                    while self.keep_running:
                        message = await websocket.receive()
                        if message.type == aiohttp.WSMsgType.TEXT:
                            await self.send_binance_message(message.data)
        except Exception as e:
            print(f"連接 Binance WebSocket 出現錯誤: {e}")

    async def send_binance_message(self, message):
        try:
            data = json.loads(message)
            price = data.get('p')
            if price:
                await self.send(text_data=json.dumps({
                    'symbol': 'BTCUSDT',
                    'price': price,
                }))
        except json.JSONDecodeError:
            print("無法解析 Binance WebSocket 消息")