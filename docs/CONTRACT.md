# Bridge Contract: Overwatch Character inside Elden Ring

Route: **Frame Compositing (Picture Transport via Named Shared Memory)**
Date: 2026-10-12
Host: Elden Ring (Steam AppID 1245620, Dantelion Engine, DirectX 12, offline EAC-disabled)
Guest: Overwatch Character Standalone Renderer (Doomfist / Genji)

---

## 1. Ownership & Authority

| Subsystem | Owner | Hand-back Trigger / Policy |
| :--- | :--- | :--- |
| **Player Movement & Physics** | Elden Ring | Host drives physical translation, ground collision, Havok movement. |
| **Camera & Viewport** | Elden Ring | Host supplies Camera Eye, View Matrix, and Projection Matrix at Present time. |
| **World Geometry & Collision**| Elden Ring | Host collision is authoritative. |
| **Character Rendering** | Guest Renderer | Guest renders character RGBA + linear depth with background cleared to transparent. |
| **Compositing & Occlusion** | Host (D3D12 Pass) | Host tests guest depth against Elden Ring's reversed-Z depth buffer before Present. |
| **Menus & Loading Screens** | Elden Ring | Guest layer is hidden when game menus / map / loading screens are active. |

---

## 2. Coordinate Mapping & Units

- **Scale**: 1 Elden Ring metre = 1 Overwatch metre (1.0 : 1.0).
- **Coordinate Transformation**:
  - Elden Ring: Y-up, X-right, Z-forward (metres).
  - Overwatch native: Z-up, X-right, Y-forward (metres).
  - Mapping function:
    $$\begin{aligned}
    X_{ER} &= X_{OW} \\
    Y_{ER} &= Z_{OW} \\
    Z_{ER} &= Y_{OW}
    \end{aligned}$$
  - Yaw: $\text{Yaw}_{ER} = \text{Yaw}_{OW}$.

---

## 3. Transport & Shared Memory Layout

- **Transport Mechanism**: Named Shared Memory (`CreateFileMapping` / `OpenFileMapping`) bound to `Local\OWPassthroughFrame`.
- **Concurrency**: Triple-buffered slot array with **Seqlock** sequence counters (odd during write, even when committed).
- **Memory Header Layout**:
  - `Magic`: `0x4F575053` (`OWPS` - Overwatch Passthrough) (4 bytes)
  - `ProtocolVersion`: `0x00010000` (4 bytes)
  - `Width`: Frame width (uint32, e.g. 1920)
  - `Height`: Frame height (uint32, e.g. 1080)
  - `ActiveSlot`: Slot index (0, 1, 2)
  - `Sequence`: Global monotonic frame counter
  - `Slots[3]`:
    - `SeqLock`: uint32 (odd = writing, even = stable)
    - `TimestampUs`: uint64 monotonic timestamp
    - `CameraPos`: float[3] (x, y, z)
    - `ViewMatrix`: row-major float[16]
    - `ProjMatrix`: row-major float[16]
    - `ColorOffset`: uint64 (byte offset to RGBA8 buffer)
    - `DepthOffset`: uint64 (byte offset to R32F depth buffer)

---

## 4. Depth & Occlusion Specification

- **Elden Ring Depth Buffer**: Reversed-Z ($1.0 = \text{near}, 0.0 = \text{far}$).
- **Guest Depth**: Linear view-space depth in metres ($Z_{\text{view}}$).
- **Depth Test Condition**:
  - Convert Elden Ring depth $D_{ER}$ to linear view distance: $Z_{host} = \frac{K}{D_{ER}}$.
  - If $Z_{guest} \le Z_{host} + \text{bias}$ and Guest Alpha $> 0.01$, draw guest pixel.
  - Otherwise, discard (occluded by pillars, walls, or terrain).

---

## 5. Lifecycle & Stale Frame Policy

- **Heartbeat & Watchdog**:
  - If host receives no new frames for $> 150\text{ ms}$, the compositor automatically drops the guest layer (cleared to transparent) to prevent frozen ghosting on screen.
- **Graceful Shutdown**:
  - Detaching the guest unmaps shared memory and restores native display flags.
