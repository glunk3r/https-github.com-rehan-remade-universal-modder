"""TDD Suite for ReShade Add-on Live Dynamic Registration and Initialization.

Tests:
1. ReShade64 (dxgi.dll) exports ReShadeRegisterAddon and ReShadeUnregisterAddon.
2. ow_compositor.addon exports AddonInit, AddonUninit, NAME, DESCRIPTION.
3. Live AddonInit execution with real ReShade runtime succeeds (returns True).
4. Auto-detection fallback: AddonInit(None, None) resolves HMODULE via GetModuleHandleExA and succeeds.
5. Addon unregisters cleanly via AddonUninit.
6. Absolute isolation: Minecraft Steve files remain untouched and identical.
"""
import ctypes
from pathlib import Path
import pytest

from tools.ow_passthrough.deploy_host import HostDeployer, DEFAULT_GAME_DIR


@pytest.fixture(scope="module")
def paths():
    base_dir = Path(__file__).resolve().parent.parent
    addon_path = base_dir / "tools" / "ow_passthrough" / "addon" / "build" / "ow_compositor.addon"
    dxgi_path = DEFAULT_GAME_DIR / "dxgi.dll"
    return {
        "addon": addon_path,
        "dxgi": dxgi_path,
        "deployed_addon": DEFAULT_GAME_DIR / "ow_compositor.addon",
        "deployed_dxgi": DEFAULT_GAME_DIR / "dxgi.dll",
    }


def test_addon_binary_exports(paths):
    addon = ctypes.WinDLL(str(paths["addon"]))
    assert hasattr(addon, "AddonInit"), "ow_compositor.addon must export AddonInit"
    assert hasattr(addon, "AddonUninit"), "ow_compositor.addon must export AddonUninit"
    assert hasattr(addon, "NAME"), "ow_compositor.addon must export NAME"
    assert hasattr(addon, "DESCRIPTION"), "ow_compositor.addon must export DESCRIPTION"


def test_reshade_runtime_exports(paths):
    dxgi = ctypes.WinDLL(str(paths["dxgi"]))
    assert hasattr(dxgi, "ReShadeRegisterAddon"), "ReShade must export ReShadeRegisterAddon"
    assert hasattr(dxgi, "ReShadeUnregisterAddon"), "ReShade must export ReShadeUnregisterAddon"


def test_live_addon_registration_explicit_handles(paths):
    dxgi = ctypes.WinDLL(str(paths["dxgi"]))
    addon = ctypes.WinDLL(str(paths["addon"]))

    addon_init = addon.AddonInit
    addon_init.restype = ctypes.c_bool
    addon_init.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

    addon_uninit = addon.AddonUninit
    addon_uninit.restype = None
    addon_uninit.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

    success = addon_init(ctypes.c_void_p(addon._handle), ctypes.c_void_p(dxgi._handle))
    assert success is True, "AddonInit with explicit handles must succeed"

    # Cleanup
    addon_uninit(ctypes.c_void_p(addon._handle), ctypes.c_void_p(dxgi._handle))


def test_live_addon_registration_auto_resolution(paths):
    dxgi = ctypes.WinDLL(str(paths["dxgi"]))
    addon = ctypes.WinDLL(str(paths["addon"]))

    addon_init = addon.AddonInit
    addon_init.restype = ctypes.c_bool
    addon_init.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

    addon_uninit = addon.AddonUninit
    addon_uninit.restype = None
    addon_uninit.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

    # Calling with nullptr mimics ReShade host loader
    success = addon_init(None, None)
    assert success is True, "AddonInit with NULL handles must auto-resolve via GetModuleHandleEx and succeed"

    addon_uninit(None, None)


def test_deployed_game_isolation():
    deployer = HostDeployer()
    assert deployer.verify_mc_intact() is True, "Minecraft project must remain 100% intact"


def test_live_shared_memory_frame_exchange(paths):
    from tools.ow_passthrough.shared_memory import SharedMemoryBridge, PoseData

    # Create shared memory transport
    bridge = SharedMemoryBridge(width=32, height=32)
    assert bridge.has_mmap is True, "Windows named shared memory mmap must be allocated"

    # Load and initialize addon with ReShade
    dxgi = ctypes.WinDLL(str(paths["dxgi"]))
    addon = ctypes.WinDLL(str(paths["addon"]))

    addon_init = addon.AddonInit
    addon_init.restype = ctypes.c_bool
    addon_init.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

    addon_uninit = addon.AddonUninit
    addon_uninit.restype = None
    addon_uninit.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

    assert addon_init(None, None) is True, "Addon registration must succeed"

    # Write test frames with seqlock
    color = b"\x22\x33\x44\xff" * (32 * 32)
    depth = b"\x00\x00\x80\x3f" * (32 * 32)  # 1.0f

    for i in range(5):
        bridge.write_frame(
            pose=PoseData((1.0, 2.0, 3.0), float(i * 10), 0.0),
            color_rgba=color,
            depth_r32f=depth,
        )

    # Read back and verify integrity
    res = bridge.read_latest_frame()
    assert res.is_valid is True, "Latest frame read must be valid under seqlock protocol"
    assert res.pose.yaw_deg == 40.0, "Latest frame yaw must match sequence"
    assert len(res.color_data) == 32 * 32 * 4
    assert len(res.depth_data) == 32 * 32 * 4

    # Cleanup
    addon_uninit(None, None)
    bridge.close()

