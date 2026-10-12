r"""OWPassthroughServer: background daemon that drives real-time frame production.

Runs the Orchestrator loop at target framerate (e.g. 60 FPS) and commits
rendered frames into the named shared memory bridge (`Local\OWPassthroughFrame`).
"""
import threading
import time
from typing import Optional

from tools.ow_passthrough.shared_memory import SharedMemoryBridge
from tools.ow_passthrough.orchestrator import PassthroughOrchestrator
from tools.ow_doomfist.input_controller import VirtualKey


class OWPassthroughServer:
    def __init__(
        self,
        width: int = 128,
        height: int = 128,
        fps: int = 60,
        bridge: Optional[SharedMemoryBridge] = None,
        hero: str = "Doomfist",
    ):
        self.width = width
        self.height = height
        self.fps = fps
        self.interval_s = 1.0 / float(fps)
        self.bridge = bridge
        self.hero_name = hero

        self.orchestrator = PassthroughOrchestrator(width=width, height=height)
        if hero != "Doomfist":
            self.orchestrator.set_hero(hero)
        if self.bridge is not None:
            self.orchestrator.shared_memory = self.bridge
            self.orchestrator.guest_renderer.bridge = self.bridge

        self.frames_produced = 0
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._key_states = {
            VirtualKey.RBUTTON: False,
            VirtualKey.LBUTTON: False,
            VirtualKey.SHIFT: False,
            VirtualKey.KEY_E: False,
            VirtualKey.KEY_Q: False,
        }

    def is_alive(self) -> bool:
        return self._running and self._thread is not None and self._thread.is_alive()

    def poll_host_inputs(self) -> None:
        """Poll host global key/mouse states via Windows GetAsyncKeyState."""
        import sys
        if sys.platform != "win32":
            return
        import ctypes
        try:
            get_key = ctypes.windll.user32.GetAsyncKeyState
        except Exception:
            return

        keys = (VirtualKey.RBUTTON, VirtualKey.LBUTTON, VirtualKey.SHIFT, VirtualKey.KEY_E, VirtualKey.KEY_Q)
        for vk in keys:
            is_down = bool(get_key(vk.value) & 0x8000)
            was_down = self._key_states.get(vk, False)
            if is_down and not was_down:
                self.orchestrator.on_key_down(vk)
                self._key_states[vk] = True
            elif not is_down and was_down:
                self.orchestrator.on_key_up(vk)
                self._key_states[vk] = False

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

            self.poll_host_inputs()
            self.orchestrator.step_frame(dt=dt)
            self.frames_produced += 1

            # Sleep to match target framerate
            elapsed = time.perf_counter() - now
            sleep_time = self.interval_s - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="OW Passthrough Shared Memory Server")
    parser.add_argument("--hero", type=str, default="Doomfist", help="Hero to render (Doomfist or Genji)")
    parser.add_argument("--fps", type=int, default=60, help="Target framerate (default: 60)")
    parser.add_argument("--width", type=int, default=128, help="Frame width (default: 128)")
    parser.add_argument("--height", type=int, default=128, help="Frame height (default: 128)")
    parser.add_argument("--duration", type=float, default=0.0, help="Run duration in seconds (0 = forever)")
    args = parser.parse_args()

    print(f"[*] Starting OW Passthrough Server: hero={args.hero}, {args.width}x{args.height} @ {args.fps} FPS")
    server = OWPassthroughServer(width=args.width, height=args.height, fps=args.fps, hero=args.hero)
    server.start()
    print("[*] Server active. Publishing to Local\\OWPassthroughFrame...")
    try:
        if args.duration > 0.0:
            time.sleep(args.duration)
        else:
            last_state = ""
            while True:
                time.sleep(0.1)
                curr_state = server.orchestrator.input_controller.current_state.name
                if curr_state != last_state:
                    print(f"\n[+] Key Input Event -> {server.hero_name} State: {curr_state}")
                    last_state = curr_state
                print(f"[*] Frames: {server.frames_produced} | State: {curr_state}    ", end="\r")
    except KeyboardInterrupt:
        print("\n[*] Stopping server...")
    finally:
        server.stop()
        print("[*] Server stopped cleanly.")


if __name__ == "__main__":
    main()
