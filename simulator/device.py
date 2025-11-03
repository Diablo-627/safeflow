import asyncio
import math
import random
import uuid
from datetime import datetime, timezone
import json


class SensorDevice:
    """
    Реалистичная модель датчика температуры SITRANS T TS500.
    Поддерживает деградацию (gradual), начальную деградацию (start_degraded),
    и случайные инциденты (spike, stuck).
    """

    def __init__(
        self,
        sensor_id: str = None,
        location: str = "plant",
        sample_interval: float = 1.0,
        env_base: float = 25.0,
        env_amplitude: float = 3.0,
        env_period_seconds: float = 24 * 3600,
        init_bias: float = 0.0,
        init_scale: float = 1.0,
        init_noise_std: float = 0.05,
        degradation_start_s: float = 3600,
        degradation_duration_s: float = 7200,
        max_bias: float = 2.0,
        max_scale_error: float = 0.05,
        max_noise_std: float = 0.5,
        spike_chance_per_sample: float = 0.0005,
        stuck_chance_per_sample: float = 1e-5,
        start_degraded: bool = False,
        initial_degradation_level: float = 0.0,
        random_seed: int = None,
    ):
        self.sensor_id = sensor_id or str(uuid.uuid4())
        self.location = location
        self.sample_interval = sample_interval

        # environment parameters
        self.env_base = env_base
        self.env_amp = env_amplitude
        self.env_period = env_period_seconds

        # initial sensor params
        self.bias = init_bias
        self.scale = init_scale
        self.noise_std = init_noise_std

        # degradation params
        self.degradation_start_s = degradation_start_s
        self.degradation_duration_s = degradation_duration_s
        self.max_bias = max_bias
        self.max_scale_error = max_scale_error
        self.max_noise_std = max_noise_std

        # fault probabilities
        self.spike_chance = spike_chance_per_sample
        self.stuck_chance = stuck_chance_per_sample

        # internal state
        self.start_time = None
        self.t = 0.0
        self.running = False
        self.is_stuck = False
        self.stuck_value = None
        self.spike_until = 0.0

        # degradation
        self.start_degraded = start_degraded
        self.degradation_level = initial_degradation_level if start_degraded else 0.0
        self._degr_initialized = False
        self._degr_bias_target = None
        self._degr_scale_target = None

        # inertia
        self.last_reading = None
        self.inertia_alpha = 0.3  # 0.0 = без инерции, 1.0 = сильная инерция

        # RNG
        self.rng = random.Random(random_seed)

    # --- Environment temperature model ---
    def _true_environment_temp(self, timestamp: float):
        phase = (timestamp % self.env_period) / self.env_period
        temp = self.env_base + self.env_amp * math.sin(2 * math.pi * phase)
        temp += self.rng.gauss(0, 0.02)
        return temp

    # --- Degradation logic ---
    def _apply_degradation(self, true_temp: float, elapsed_s: float):
        if elapsed_s < self.degradation_start_s:
            prog = self.degradation_level
        else:
            progress_time = elapsed_s - self.degradation_start_s
            prog = min(1.0, (progress_time / self.degradation_duration_s) ** 1.2)

        if not self._degr_initialized and elapsed_s >= self.degradation_start_s:
            self._degr_bias_target = self.max_bias * (
                1 if self.rng.random() > 0.5 else -1
            )
            scale_dir = 1 if self.rng.random() > 0.5 else -1
            self._degr_scale_target = 1.0 + (self.max_scale_error * scale_dir)
            self._degr_initialized = True

        bias_target = self._degr_bias_target if self._degr_initialized else 0.0
        scale_target = self._degr_scale_target if self._degr_initialized else 1.0

        current_bias = self.bias + prog * bias_target
        current_scale = self.scale + prog * (scale_target - self.scale)
        current_noise = self.noise_std + prog * (self.max_noise_std - self.noise_std)

        return current_bias, current_scale, current_noise, prog

    # --- Faults (spike, stuck) ---
    def _maybe_trigger_faults(self, elapsed_s: float):
        fault = None
        if self.rng.random() < self.spike_chance:
            self.spike_until = elapsed_s + self.rng.uniform(1, 5)
            fault = ("spike", self.spike_until)
        if not self.is_stuck and self.rng.random() < self.stuck_chance:
            self.is_stuck = True
            self.stuck_value = None
            fault = ("stuck", None)
        return fault

    # --- Main sampling ---
    def single_sample(self, epoch_ts: float = None):
        if epoch_ts is None:
            epoch_ts = datetime.now(timezone.utc).timestamp()
        if self.start_time is None:
            self.start_time = epoch_ts
        elapsed = epoch_ts - self.start_time
        self.t = elapsed

        true_temp = self._true_environment_temp(epoch_ts)
        self._maybe_trigger_faults(elapsed)
        current_bias, current_scale, current_noise, prog = self._apply_degradation(
            true_temp, elapsed
        )

        reading = (
            true_temp * current_scale + current_bias + self.rng.gauss(0, current_noise)
        )

        fault_type = None
        if elapsed < self.spike_until:
            reading += self.rng.uniform(5.0, 20.0) * (
                1 if self.rng.random() > 0.5 else -1
            )
            fault_type = "spike"
        if self.is_stuck:
            if self.stuck_value is None:
                self.stuck_value = reading
            reading = self.stuck_value
            fault_type = "stuck"

        if self.last_reading is not None:
            reading = self.last_reading * self.inertia_alpha + reading * (
                1 - self.inertia_alpha
            )
        self.last_reading = reading

        if prog < 0.05:
            health_state = "healthy"
        elif prog < 0.4:
            health_state = "slightly_degraded"
        elif prog < 0.8:
            health_state = "degrading"
        else:
            health_state = "critical"

        return {
            "timestamp": datetime.fromtimestamp(epoch_ts, tz=timezone.utc).isoformat(),
            "sensor_id": self.sensor_id,
            "location": self.location,
            "sample_interval": self.sample_interval,
            "true_temp": round(true_temp, 4),
            "reading": round(reading, 4),
            "params": {
                "bias": round(current_bias, 4),
                "scale": round(current_scale, 6),
                "noise_std": round(current_noise, 6),
            },
            "health_state": health_state,
            "degradation_level": round(prog, 4),
            "fault_type": fault_type,
        }

    # --- Async runner ---
    async def run_to_file(
        self,
        out_path: str,
        stop_after_s: float = None,
        max_samples: int = None,
        mqtt_publisher=None,
        field_mode: bool = False,  # <--- добавлено
    ):
        """Запуск симуляции. Если field_mode=True — создаются боевые данные без меток."""
        self.running = True
        samples = 0
        with open(out_path, "a", buffering=1) as f:
            while self.running:
                ts = datetime.now(timezone.utc).timestamp()
                sample = self.single_sample(ts)

                # === Убираем служебные поля в "боевом" режиме ===
                if field_mode:
                    sample.pop("health_state", None)
                    sample.pop("degradation_level", None)
                    sample.pop("fault_type", None)
                    sample.pop("params", None)

                f.write(json.dumps(sample, ensure_ascii=False) + "\n")
                f.flush()

                if mqtt_publisher:
                    try:
                        await mqtt_publisher.publish(
                            json.dumps(sample, ensure_ascii=False)
                        )
                    except Exception:
                        pass

                samples += 1
                if max_samples is not None and samples >= max_samples:
                    break
                if stop_after_s is not None and self.t >= stop_after_s:
                    break
                await asyncio.sleep(self.sample_interval)
        self.running = False

    def stop(self):
        self.running = False
