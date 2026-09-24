#!/usr/bin/env python3
"""Chat de IA do eazy via API compatível com OpenRouter."""
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "gryphe/mythomax-l2-13b"


def load_env_file():
    path = os.environ.get("EAZY_AI_ENV", os.path.expanduser("~/.config/eazy/ai.env"))
    try:
        with open(path, encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip("'\"")
                if key in {"OPENROUTER_API_KEY", "EAZY_AI_API_KEY", "EAZY_AI_URL", "EAZY_AI_MODEL"}:
                    os.environ.setdefault(key, value)
    except OSError:
        pass


def ask(url, model, api_key, messages):
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": float(os.environ.get("EAZY_AI_TEMPERATURE", "0.7")),
        "max_tokens": int(os.environ.get("EAZY_AI_MAX_TOKENS", "1000")),
    }).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/vapesmadcat-blip/Easy_Player",
            "X-Title": "eazy",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        data = json.load(response)
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"resposta inesperada da API: {data}") from exc


def main():
    load_env_file()
    api_key = os.environ.get("EAZY_AI_API_KEY") or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("IA não configurada: defina EAZY_AI_API_KEY ou OPENROUTER_API_KEY.", file=sys.stderr)
        print("Você também pode usar ~/.config/eazy/ai.env (permissão 600).", file=sys.stderr)
        return 2
    url = os.environ.get("EAZY_AI_URL", DEFAULT_URL)
    model = os.environ.get("EAZY_AI_MODEL", DEFAULT_MODEL)
    messages = []
    print(f"eazy IA — modelo: {model}")
    print("Digite 'sair' para fechar.\n")
    while True:
        try:
            user_input = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando.")
            return 0
        if not user_input:
            continue
        if user_input.lower() in {"sair", "exit", "quit"}:
            return 0
        messages.append({"role": "user", "content": user_input})
        try:
            answer = ask(url, model, api_key, messages)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:500]
            print(f"\nErro da API ({exc.code}): {detail}\n")
            messages.pop()
            continue
        except (urllib.error.URLError, TimeoutError, ValueError, RuntimeError) as exc:
            print(f"\nErro de conexão/API: {exc}\n")
            messages.pop()
            continue
        messages.append({"role": "assistant", "content": answer})
        print(f"\nIA: {answer}\n")


if __name__ == "__main__":
    raise SystemExit(main())
