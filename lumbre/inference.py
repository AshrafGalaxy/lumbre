"""Call a hosted open-weight model. Weights load only on a Hugging Face Space."""

import os
import threading
from typing import Any

import requests

from lumbre.config import (
    FALLBACK_SPACE_MODEL,
    HOSTED_MODEL,
    HOSTED_URL,
    ROUTER_URL,
    Settings,
)

_LOCK = threading.Lock()
_WEIGHTS: dict[str, Any] = {}


class InferenceError(Exception):
    """The model host did not return a card."""


def generate(system: str, user: str, settings: Settings) -> tuple[str, str]:
    if settings.backend == "weights":
        return _generate_weights(system, user, settings)
    if settings.backend == "router":
        return _generate_router(system, user, settings)
    return _generate_hosted(system, user)


def _generate_hosted(system: str, user: str) -> tuple[str, str]:
    try:
        response = requests.post(
            HOSTED_URL,
            json={
                "model": HOSTED_MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0.2,
                "max_tokens": 280,
            },
            timeout=45,
        )
    except requests.RequestException as exc:
        raise InferenceError("The model host could not be reached.") from exc
    if response.status_code == 429:
        raise InferenceError("The host allows two cards a minute. Wait a moment and try again.")
    if response.status_code >= 400:
        raise InferenceError(f"The model host returned {response.status_code}.")
    try:
        payload = response.json()
        text = str(payload["choices"][0]["message"].get("content") or "").strip()
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise InferenceError("The model host returned an unexpected reply.") from exc
    if not text:
        raise InferenceError("The model returned an empty reply.")
    model = str(payload.get("model") or HOSTED_MODEL)
    return text, model


def _generate_router(system: str, user: str, settings: Settings) -> tuple[str, str]:
    if not settings.hf_token:
        raise InferenceError("Add HF_TOKEN to a local .env file. The file is gitignored.")
    try:
        response = requests.post(
            ROUTER_URL,
            headers={
                "Authorization": f"Bearer {settings.hf_token}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.router_model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0.2,
                "max_tokens": 320,
            },
            timeout=90,
        )
    except requests.RequestException as exc:
        raise InferenceError("The model host could not be reached.") from exc
    if response.status_code == 402:
        raise InferenceError(
            "This Hugging Face account has no Inference Providers credits. "
            "Leave LUMBRE_BACKEND unset to use the hosted open model."
        )
    if response.status_code >= 400:
        detail = _safe_detail(response.text, settings.hf_token)
        raise InferenceError(f"The model host returned {response.status_code}. {detail}")
    try:
        payload = response.json()
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise InferenceError("The model host returned an unexpected reply.") from exc
    text = _content_text(content)
    model = str(payload.get("model") or settings.router_model)
    if not text:
        raise InferenceError("The model returned an empty reply.")
    return text, model


def _generate_weights(system: str, user: str, settings: Settings) -> tuple[str, str]:
    import torch

    with _LOCK:
        tokenizer, model, model_id = _load_weights(settings)
        messages = [{"role": "user", "content": f"{system}\n\n{user}"}]
        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        inputs = tokenizer(prompt, return_tensors="pt")
        input_length = inputs["input_ids"].shape[-1]
        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_new_tokens=280,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
            )
        reply = tokenizer.decode(output[0][input_length:], skip_special_tokens=True)
    text = reply.strip()
    if not text:
        raise InferenceError("The model returned an empty reply.")
    return text, model_id


def _load_weights(settings: Settings) -> tuple[Any, Any, str]:
    if _WEIGHTS:
        return _WEIGHTS["tokenizer"], _WEIGHTS["model"], _WEIGHTS["model_id"]
    errors: list[str] = []
    for model_id in _candidates(settings):
        try:
            tokenizer, model = _from_pretrained(model_id)
        except Exception as exc:
            errors.append(f"{model_id}: {_safe_detail(str(exc), settings.hf_token)}")
            continue
        _WEIGHTS["tokenizer"] = tokenizer
        _WEIGHTS["model"] = model
        _WEIGHTS["model_id"] = model_id
        return tokenizer, model, model_id
    joined = " ".join(errors)[:500]
    raise InferenceError(f"The open model could not be loaded. {joined}")


def _candidates(settings: Settings) -> list[str]:
    ordered = [settings.space_model]
    if FALLBACK_SPACE_MODEL not in ordered:
        ordered.append(FALLBACK_SPACE_MODEL)
    return ordered


def _from_pretrained(model_id: str) -> tuple[Any, Any]:
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float32)
    model.eval()
    return tokenizer, model


def _content_text(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("text"):
                parts.append(str(item["text"]))
        return "\n".join(parts).strip()
    return str(content).strip()


def _safe_detail(text: str, token: str) -> str:
    cleaned = " ".join(text.split())
    if token:
        cleaned = cleaned.replace(token, "[token]")
    return cleaned[:240]
