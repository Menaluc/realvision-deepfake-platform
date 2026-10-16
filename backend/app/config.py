"""App settings, read once from the environment (prefix REALVISION_)."""

import os
from dataclasses import dataclass
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]

ENV_PREFIX = "REALVISION_"


@dataclass(frozen=True)
class Settings:
    checkpoint_path: Path = BACKEND_DIR / "models" / "baseline_best.pt"
    # "cpu" unless CUDA is configured explicitly
    device: str = "cpu"
    cache_max_entries: int = 20
    cache_ttl_seconds: float = 30 * 60

    @classmethod
    def from_env(cls) -> "Settings":
        defaults = cls()

        def read(name, default, parse):
            value = os.environ.get(ENV_PREFIX + name)
            return default if value is None else parse(value)

        return cls(
            checkpoint_path=read("CHECKPOINT_PATH", defaults.checkpoint_path, Path),
            device=read("DEVICE", defaults.device, str),
            cache_max_entries=read(
                "CACHE_MAX_ENTRIES", defaults.cache_max_entries, int
            ),
            cache_ttl_seconds=read(
                "CACHE_TTL_SECONDS", defaults.cache_ttl_seconds, float
            ),
        )
