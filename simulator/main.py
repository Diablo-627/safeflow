# main.py
import asyncio
import argparse
import os
import logging
from simulator.scenarios import (
    healthy_then_degrade,
    immediately_degraded,
    intermittent_spikes,
    stuck_after_time,
    realistic_field_data,
)
from simulator.producer_mqtt import get_publisher

# === Настройки логирования ===
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

# === Сценарии ===
SCENARIOS = {
    "healthy_then_degrade": healthy_then_degrade,
    "immediately_degraded": immediately_degraded,
    "intermittent_spikes": intermittent_spikes,
    "stuck_after_time": stuck_after_time,
    "realistic_field_data": realistic_field_data,
}


# === Основная задача симуляции ===
async def run_sensor_task(
    sensor_factory,
    out_path,
    run_seconds=None,
    max_samples=None,
    mqtt_broker=None,
):
    """Запускает один симулятор датчика и сохраняет поток данных."""
    sensor = sensor_factory()
    publisher = None
    pub_ctx = None

    # --- если указан MQTT брокер ---
    if mqtt_broker:
        pub_ctx = get_publisher(mqtt_broker)
        try:
            await pub_ctx.__aenter__()
            publisher = pub_ctx
            logging.info(f"Подключено к MQTT брокеру: {mqtt_broker}")
        except Exception as e:
            logging.error(f"Не удалось подключиться к MQTT брокеру: {e}")
            publisher = None

    # --- основной цикл записи данных ---
    try:
        await sensor.run_to_file(
            out_path,
            stop_after_s=run_seconds,
            max_samples=max_samples,
            mqtt_publisher=publisher,
        )
    finally:
        if pub_ctx:
            await pub_ctx.__aexit__(None, None, None)


# === Асинхронная точка входа ===
async def main_async(args):
    out_dir = os.path.dirname(args.out_file)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    logging.info(f"Запуск сценария: {args.scenario}")
    logging.info(f"Количество сенсоров: {args.sensor_count}")
    logging.info(f"Выходной файл: {args.out_file}")
    if args.mqtt:
        logging.info(f"MQTT брокер: {args.mqtt}")

    tasks = []
    for i in range(args.sensor_count):
        scen_key = args.scenario
        if scen_key not in SCENARIOS:
            raise SystemExit(f"Неизвестный сценарий: {scen_key}")

        # создаём фабрику с уникальным sensor_id
        factory = lambda sid=f"sensor_{i}_{scen_key}": SCENARIOS[scen_key](
            sensor_id=sid
        )

        # для нескольких сенсоров — уникальные файлы
        out_file = (
            args.out_file
            if args.sensor_count == 1
            else args.out_file.replace(".ndjson", f"_{i}.ndjson")
        )

        tasks.append(
            asyncio.create_task(
                run_sensor_task(
                    factory,
                    out_file,
                    run_seconds=args.run_seconds,
                    max_samples=args.max_samples,
                    mqtt_broker=args.mqtt,
                )
            )
        )

    await asyncio.gather(*tasks)


# === Парсер аргументов ===
def parse_args():
    p = argparse.ArgumentParser(description="SITRANS T TS500 simulator")
    p.add_argument(
        "--scenario", default="healthy_then_degrade", choices=list(SCENARIOS.keys())
    )
    p.add_argument("--out-file", default="sim_output.ndjson")
    p.add_argument(
        "--run-seconds", type=float, default=None, help="stop after N seconds"
    )
    p.add_argument(
        "--max-samples", type=int, default=None, help="stop after N samples per sensor"
    )
    p.add_argument(
        "--sensor-count", type=int, default=1, help="number of sensors to spawn"
    )
    p.add_argument(
        "--mqtt",
        type=str,
        default=None,
        help="mqtt broker host:port to publish to (optional)",
    )
    return p.parse_args()


# === Точка входа ===
if __name__ == "__main__":
    args = parse_args()
    try:
        asyncio.run(main_async(args))
    except KeyboardInterrupt:
        print("⛔ Остановлено пользователем")
