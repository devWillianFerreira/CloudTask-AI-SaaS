#!/usr/bin/env python3
"""Semana 5 · Aula 9 — Teste de carga simples com autenticação JWT.

Dispara muitas requisições HTTP em paralelo contra um endpoint durante alguns
segundos e, ao final, imprime um resumo.

Suporta autenticação via Bearer Token:
    --token SEU_TOKEN

Exemplo:

    python scripts/hpa/teste-carga.py \
        --url http://localhost:8000/tasks \
        --concurrency 100 \
        --duration 300 \
        --token SEU_TOKEN
"""

from __future__ import annotations

import argparse
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field


@dataclass
class Stats:
    """Acumula os resultados das requisições."""

    ok: int = 0
    errors: int = 0
    total_latency: float = 0.0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def record_ok(self, latency: float) -> None:
        with self._lock:
            self.ok += 1
            self.total_latency += latency

    def record_error(self) -> None:
        with self._lock:
            self.errors += 1

    @property
    def total(self) -> int:
        return self.ok + self.errors

    @property
    def avg_latency_ms(self) -> float:
        return (self.total_latency / self.ok * 1000) if self.ok else 0.0


def _worker(
    url: str,
    deadline: float,
    timeout: float,
    stats: Stats,
    token: str | None,
) -> None:

    while time.monotonic() < deadline:

        headers = {}

        if token:
            headers["Authorization"] = f"Bearer {token}"

        request = urllib.request.Request(
            url,
            headers=headers,
            method="GET"
        )

        start = time.monotonic()

        try:
            with urllib.request.urlopen(
                request,
                timeout=timeout
            ) as resp:

                resp.read()

                if 200 <= resp.status < 400:
                    stats.record_ok(
                        time.monotonic() - start
                    )
                else:
                    stats.record_error()

        except (
            urllib.error.URLError,
            OSError,
            ValueError
        ):
            stats.record_error()


def run_load_test(
    url: str,
    concurrency: int,
    duration: float,
    timeout: float = 5.0,
    token: str | None = None,
) -> Stats:
    """Executa o teste de carga."""

    stats = Stats()

    deadline = time.monotonic() + duration

    threads = [
        threading.Thread(
            target=_worker,
            args=(
                url,
                deadline,
                timeout,
                stats,
                token,
            ),
            daemon=True,
        )
        for _ in range(concurrency)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    return stats


def _parse_args(
    argv: list[str] | None = None
) -> argparse.Namespace:

    parser = argparse.ArgumentParser(
        description="Teste de carga simples para acionar o HPA."
    )

    parser.add_argument(
        "--url",
        required=True,
        help="Endpoint alvo"
    )

    parser.add_argument(
        "--concurrency",
        type=int,
        default=20,
        help="Clientes simultâneos"
    )

    parser.add_argument(
        "--duration",
        type=float,
        default=30.0,
        help="Duração do teste em segundos"
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Timeout por requisição"
    )

    parser.add_argument(
        "--token",
        help="Token JWT para autenticação Bearer"
    )

    args = parser.parse_args(argv)

    if args.concurrency < 1:
        parser.error("--concurrency deve ser >= 1")

    if args.duration <= 0:
        parser.error("--duration deve ser > 0")

    return args


def main(
    argv: list[str] | None = None
) -> int:

    args = _parse_args(argv)

    print(
        f"Carga: {args.concurrency} clientes x "
        f"{args.duration:.0f}s contra {args.url}",
        flush=True,
    )

    if args.token:
        print("Autenticação: Bearer Token habilitado", flush=True)
    else:
        print("Autenticação: sem token", flush=True)


    started = time.monotonic()

    stats = run_load_test(
        args.url,
        args.concurrency,
        args.duration,
        args.timeout,
        args.token,
    )

    elapsed = time.monotonic() - started


    rps = stats.total / elapsed if elapsed else 0.0


    print("\n--- Resultado ---")
    print(f"Total de requisições : {stats.total}")
    print(f"  OK (2xx/3xx)       : {stats.ok}")
    print(f"  Erros              : {stats.errors}")
    print(f"Tempo decorrido      : {elapsed:.1f}s")
    print(f"Requisições/segundo  : {rps:.1f}")
    print(f"Latência média (OK)  : {stats.avg_latency_ms:.1f} ms")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())