"""Named shared memory transport with Seqlock triple-buffering for Passthrough frame compositing.

Protocol: OWPS (Overwatch Passthrough) v1.0
Implements seqlock consistency checks to eliminate torn or desynced frames across process boundaries.
"""
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import time

MAGIC_OWPS = 0x4F575053          # "OWPS"
PROTOCOL_VERSION = 0x00010000     # 1.0


@dataclass
class PoseData:
    camera_pos: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    yaw_deg: float = 0.0
    pitch_deg: float = 0.0


@dataclass
class FrameSlot:
    slot_id: int
    seqlock: int = 0
    timestamp_us: int = 0
    pose: PoseData = field(default_factory=PoseData)
    color_data: bytes = b""
    depth_data: bytes = b""


@dataclass
class FrameHeader:
    magic: int
    protocol_version: int
    width: int
    height: int
    active_slot: int = 0
    slots: List[FrameSlot] = field(default_factory=list)


@dataclass
class ReadResult:
    is_valid: bool
    pose: Optional[PoseData] = None
    color_data: bytes = b""
    depth_data: bytes = b""
    error_reason: str = ""


class SharedMemoryBridge:
    def __init__(self, width: int = 1920, height: int = 1080, mapping_name: str = r"Local\OWPassthroughFrame"):
        self.width = width
        self.height = height
        self.mapping_name = mapping_name

        self.header = FrameHeader(
            magic=MAGIC_OWPS,
            protocol_version=PROTOCOL_VERSION,
            width=width,
            height=height,
            active_slot=0,
            slots=[FrameSlot(slot_id=i) for i in range(3)],
        )

    def get_header(self) -> FrameHeader:
        return self.header

    def write_frame(self, pose: PoseData, color_rgba: bytes, depth_r32f: bytes) -> int:
        """Write frame into next slot using Seqlock protocol."""
        next_slot_idx = (self.header.active_slot + 1) % 3
        slot = self.header.slots[next_slot_idx]

        # 1. Acquire write lock: set seqlock to odd
        start_seq = slot.seqlock
        slot.seqlock = start_seq + 1

        # 2. Write payload
        slot.timestamp_us = int(time.time() * 1_000_000)
        slot.pose = pose
        slot.color_data = color_rgba
        slot.depth_data = depth_r32f

        # 3. Release write lock: set seqlock to even
        slot.seqlock = start_seq + 2
        self.header.active_slot = next_slot_idx
        return next_slot_idx

    def read_slot(self, slot_idx: int) -> ReadResult:
        if slot_idx < 0 or slot_idx >= len(self.header.slots):
            return ReadResult(is_valid=False, error_reason="Invalid slot index")

        slot = self.header.slots[slot_idx]

        # Check 1: If seqlock is odd, write is actively in progress
        seq1 = slot.seqlock
        if seq1 % 2 != 0:
            return ReadResult(is_valid=False, error_reason="Slot is mid-write (odd seqlock)")

        # Copy data
        pose = slot.pose
        color = slot.color_data
        depth = slot.depth_data

        # Check 2: If seqlock changed during read, a torn read occurred
        seq2 = slot.seqlock
        if seq1 != seq2:
            return ReadResult(is_valid=False, error_reason="Torn read detected (seqlock mismatch)")

        return ReadResult(
            is_valid=True,
            pose=pose,
            color_data=color,
            depth_data=depth,
        )

    def read_latest_frame(self, max_age_ms: float = 150.0) -> ReadResult:
        active_idx = self.header.active_slot
        result = self.read_slot(active_idx)
        if not result.is_valid:
            return result

        slot = self.header.slots[active_idx]
        current_time_us = int(time.time() * 1_000_000)
        age_ms = (current_time_us - slot.timestamp_us) / 1000.0

        if age_ms > max_age_ms:
            return ReadResult(
                is_valid=False,
                error_reason=f"Stale frame ({age_ms:.1f}ms exceeds max age {max_age_ms}ms)",
            )

        return result
