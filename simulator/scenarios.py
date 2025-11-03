# scenarios.py
from .device import SensorDevice
import random


def healthy_then_degrade(sensor_id=None):
    return SensorDevice(
        sensor_id=sensor_id,
        sample_interval=1.0,
        env_base=25.0,
        env_amplitude=4.0,
        degradation_start_s=60 * 3,
        degradation_duration_s=60 * 5,
        max_bias=2.0,
        max_scale_error=0.05,
        max_noise_std=0.3,
        spike_chance_per_sample=0.0005,
        stuck_chance_per_sample=1e-5,
        start_degraded=False,
        random_seed=random.randint(0, 10**6),
        include_health=False,  # ⚡ боевой режим: без health_state
    )


def immediately_degraded(sensor_id=None):
    return SensorDevice(
        sensor_id=sensor_id,
        sample_interval=1.0,
        env_base=25.0,
        env_amplitude=4.0,
        degradation_start_s=0,
        degradation_duration_s=60 * 60,
        max_bias=3.0,
        max_scale_error=0.1,
        max_noise_std=0.6,
        start_degraded=True,
        initial_degradation_level=0.4,
        spike_chance_per_sample=0.001,
        stuck_chance_per_sample=3e-5,
        include_health=False,
    )

def intermittent_spikes(sensor_id=None):
    return SensorDevice(
        sensor_id=sensor_id,
        sample_interval=1.0,
        env_base=25.0,
        env_amplitude=2.5,
        degradation_start_s=60 * 30,
        degradation_duration_s=60 * 60,
        max_bias=1.0,
        max_scale_error=0.02,
        max_noise_std=0.2,
        spike_chance_per_sample=0.01,
        stuck_chance_per_sample=1e-6,
        start_degraded=False,
        random_seed=random.randint(0, 10**6),
        include_health=False
    )

def stuck_after_time(sensor_id=None):
    """
    Сценарий: через некоторое время датчик «залипает» на значении.
    """
    return SensorDevice(
        sensor_id=sensor_id,
        sample_interval=1.0,
        env_base=25.0,
        env_amplitude=3.5,
        degradation_start_s=60 * 15,
        degradation_duration_s=60 * 60,
        max_bias=1.5,
        max_scale_error=0.03,
        max_noise_std=0.25,
        spike_chance_per_sample=0.0005,
        stuck_chance_per_sample=0.001,
        start_degraded=False,
        random_seed=random.randint(0, 10**6),
        include_health=False
    )


def realistic_field_data(sensor_id=None):
    """
    Сценарий: датчик здоровый → постепенно дрейфует (аналогично healthy_then_degrade),
    без дополнительных боевых флагов.
    """

    return SensorDevice(
        sensor_id=sensor_id,
        sample_interval=1.0,
        env_base=25.0,
        env_amplitude=4.0,
        degradation_start_s=60 * 3,        # через 3 минуты начнётся деградация
        degradation_duration_s=60 * 5,     # деградация длится 5 минут
        max_bias=2.0,
        max_scale_error=0.05,
        max_noise_std=0.3,
        spike_chance_per_sample=0.0005,
        stuck_chance_per_sample=1e-5,
        start_degraded=False,
        random_seed=random.randint(0, 10**6),
    )
