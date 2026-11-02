import os
import time
from contextlib import contextmanager

class Observability:
    """
    Camada simples de observabilidade.
    Se as chaves do Langfuse não estiverem configuradas, funciona como no-op
    e não interrompe a aplicação.
    """

    def __init__(self):
        self.enabled = False
        self.client = None
        self._init_client()

    def _init_client(self):
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "").strip()
        secret_key = os.getenv("LANGFUSE_SECRET_KEY", "").strip()
        if not public_key or not secret_key:
            return
        try:
            from langfuse import get_client
            self.client = get_client()
            self.enabled = True
        except Exception:
            self.client = None
            self.enabled = False

    @contextmanager
    def trace(self, name, input_data=None, metadata=None):
        started = time.perf_counter()
        if not self.enabled or self.client is None:
            holder = {
                "enabled": False,
                "name": name,
                "input": input_data,
                "metadata": metadata or {},
                "started": started,
            }
            yield holder
            return

        try:
            with self.client.start_as_current_observation(
                as_type="span",
                name=name,
                input=input_data,
                metadata=metadata or {},
            ) as span:
                holder = {
                    "enabled": True,
                    "span": span,
                    "started": started,
                }
                yield holder
        except Exception:
            holder = {
                "enabled": False,
                "name": name,
                "input": input_data,
                "metadata": metadata or {},
                "started": started,
            }
            yield holder

    @contextmanager
    def span(self, name, input_data=None, metadata=None):
        if not self.enabled or self.client is None:
            yield None
            return
        try:
            with self.client.start_as_current_observation(
                as_type="span",
                name=name,
                input=input_data,
                metadata=metadata or {},
            ) as span:
                yield span
        except Exception:
            yield None

    def finish(self, holder, output=None, metadata=None):
        if holder and holder.get("enabled") and holder.get("span") is not None:
            try:
                elapsed_ms = round((time.perf_counter() - holder["started"]) * 1000, 2)
                combined = dict(metadata or {})
                combined["latency_ms"] = elapsed_ms
                holder["span"].update(output=output, metadata=combined)
            except Exception:
                pass

    def flush(self):
        if self.enabled and self.client is not None:
            try:
                self.client.flush()
            except Exception:
                pass
