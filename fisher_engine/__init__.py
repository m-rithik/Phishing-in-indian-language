"""Fisher's deterministic, standard-library-only synthetic E0 engine."""

from __future__ import annotations

from importlib import import_module
from typing import Any


_EXPORTS = {
    "EngineValidationContext": (".artifacts", "EngineValidationContext"),
    "EngineInputDescriptor": (".preflight", "EngineInputDescriptor"),
    "SuppliedVMPArtifact": (".preflight", "SuppliedVMPArtifact"),
    "SyntheticE0Result": (".harness", "SyntheticE0Result"),
    "ValidatedEngineEnvelope": (".artifacts", "ValidatedEngineEnvelope"),
    "ValidatedPreflightContext": (".preflight", "ValidatedPreflightContext"),
    "engine_run_envelope_sha256": (".artifacts", "engine_run_envelope_sha256"),
    "preflight_engine_input": (".preflight", "preflight_engine_input"),
    "run_synthetic_e0": (".harness", "run_synthetic_e0"),
    "run_synthetic_e0_bytes": (".harness", "run_synthetic_e0_bytes"),
    "system_artifact_manifest_sha256": (".artifacts", "system_artifact_manifest_sha256"),
    "validate_engine_envelope": (".artifacts", "validate_engine_envelope"),
    "validate_engine_envelope_bytes": (".artifacts", "validate_engine_envelope_bytes"),
    "validate_pass_preflight_context": (".preflight", "validate_pass_preflight_context"),
}


def __getattr__(name: str) -> Any:
    target = _EXPORTS.get(name)
    if target is None:
        raise AttributeError(name)
    value = getattr(import_module(target[0], __name__), target[1])
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted((*globals(), *_EXPORTS))


__all__ = list(_EXPORTS)
