"""Training configuration tests."""

from pathlib import Path

from app.config.training import TrainingSettings, get_training_settings
from app.training.constants import DEFAULT_METRIC_NAMES


class TestTrainingSettings:
    def test_default_sft_settings(self):
        settings = TrainingSettings()
        assert settings.sft_output_dir == Path("data/sft")
        assert settings.sft_val_ratio == 0.1
        assert settings.sft_seed == 42
        assert settings.sft_instruction

    def test_default_eval_settings(self):
        settings = TrainingSettings()
        assert settings.eval_output_dir == Path("data/eval_reports")
        assert settings.eval_metrics == list(DEFAULT_METRIC_NAMES)
        assert settings.eval_calibration_bins == 10
        assert settings.eval_calibration_pass_threshold == 0.25

    def test_get_training_settings_is_cached(self):
        assert get_training_settings() is get_training_settings()
