r"""OWPassthroughServer: background daemon that drives real-time frame production.

Runs the Orchestrator loop at target framerate (e.g. 60 FPS) and commits
rendered frames into the named shared memory bridge (`Local\OWPassthroughFrame`).
"""
import threading
import time
from typing import Optional

from tools.ow_passthrough.shared_memory import SharedMemoryBridge
from tools.ow_passthrough.orchestrator import PassthroughOrchestrator


class OWPassthroughServer:
    def __init__(self, width: int = 128, height: int = 128, fps: int = 60, bridge: Optional[SharedMemoryBridge] = None):
        self.width = width
        self.height = height
        self.fps = fps
        self.interval_s = 1.0 / float(fps)
        self.bridge = bridge

        self.orchestrator = PassthroughOrchestrator(width=width, height=height)
        if self.bridge is not None:
            self.orchestrator.shared_memory = self.bridge
            self.orchestrator.guest_renderer.bridge = self.bridge

        self.frames_produced = 0
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def is_alive(self) -> bool:
        return self._running and self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self.orchestrator.start()
        self._thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None
        self.orchestrator.stop()

    def _worker_loop(self) -> None:
        last_time = time.perf_counter()
        while self._running:
            now = time.perf_counter()
            dt = now - last_time
            last_time = now

            self.orchestrator.step_frame(dt=dt)
            self.frames_produced += 1

            # Sleep to match target framerate
            elapsed = time.perf_counter() - now
            sleep_time = self.interval_s - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
