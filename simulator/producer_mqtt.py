# producer_mqtt.py
import asyncio
import json
from urllib.parse import urlparse

try:
    from aiomqtt import Client as MQTTClient
    ASYNC_MQTT_AVAILABLE = True
except Exception:
    ASYNC_MQTT_AVAILABLE = False


class DummyPublisher:
    """Фейковый издатель (если MQTT не используется)"""
    async def publish(self, payload: str):
        await asyncio.sleep(0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class MQTTPublisher:
    """Асинхронный MQTT издатель с авто-переподключением"""
    def __init__(self, broker_host="localhost", broker_port=1883, topic="sensors/temperature", reconnect_delay=3):
        if not ASYNC_MQTT_AVAILABLE:
            raise RuntimeError("aiomqtt not available. Install 'aiomqtt' package.")
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topic = topic
        self.client = None
        self.reconnect_delay = reconnect_delay
        self._connected = False

    async def __aenter__(self):
        await self._connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._disconnect()

    async def _connect(self):
        """Подключение с ретраями"""
        while not self._connected:
            try:
                self.client = MQTTClient(self.broker_host, self.broker_port)
                await self.client.connect()
                self._connected = True
                print(f"[MQTT] Connected to {self.broker_host}:{self.broker_port}")
            except Exception as e:
                print(f"[MQTT] Connection failed: {e}, retrying in {self.reconnect_delay}s")
                await asyncio.sleep(self.reconnect_delay)

    async def _disconnect(self):
        """Безопасное отключение"""
        if self.client:
            try:
                await self.client.disconnect()
                print("[MQTT] Disconnected.")
            except Exception:
                pass
        self._connected = False

    async def publish(self, payload: str):
        """Публикация сообщения (автопереподключение при сбое)"""
        if not self._connected:
            await self._connect()
        try:
            await self.client.publish(self.topic, payload.encode("utf-8"))
        except Exception as e:
            print(f"[MQTT] Publish failed: {e}, reconnecting...")
            self._connected = False
            await asyncio.sleep(self.reconnect_delay)
            await self._connect()


def get_publisher(broker_url=None, topic="sensors/temperature"):
    """
    Возвращает асинхронного издателя (MQTTPublisher или DummyPublisher).
    broker_url формат: mqtt://host:port или host:port
    """
    if broker_url is None:
        return DummyPublisher()

    if not ASYNC_MQTT_AVAILABLE:
        raise RuntimeError("aiomqtt not installed. To enable MQTT, install 'aiomqtt'.")

    parsed = urlparse(broker_url)
    host_port = parsed.netloc or parsed.path or broker_url
    if host_port.startswith("//"):
        host_port = host_port.lstrip("/")

    if ":" in host_port:
        host, port_s = host_port.rsplit(":", 1)
        try:
            port = int(port_s)
        except ValueError:
            raise ValueError(f"Invalid MQTT port in broker_url: {broker_url}")
    else:
        host = host_port
        port = 1883

    return MQTTPublisher(host, port, topic)
