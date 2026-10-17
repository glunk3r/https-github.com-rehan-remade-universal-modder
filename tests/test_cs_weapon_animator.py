import pytest
import math
import numpy as np
from pathlib import Path

from tools.cs2.animator import (
    CSWeaponState,
    CSWeaponAnimator,
    AnimationClip,
    SkeletonPose,
)


@pytest.fixture
def butterfly_knife_paths():
    base = Path("./build/cs2assets/butterfly_knife")
    return {
        "model": base / "weapons/models/knife/knife_butterfly/weapon_knife_butterfly.glb",
        "draw_clip": base / "clips/animation/anims/viewmodel/knife/knife_butterfly/draw_butterfly.glb",
        "inspect_clip": base / "clips/animation/anims/viewmodel/knife/knife_butterfly/lookat02_butterfly.glb",
        "backstab_clip": base / "clips/animation/anims/viewmodel/knife/knife_butterfly/heavy_backstab_butterfly.glb",
        "arms_model": Path("./build/cs2assets/viewmodel_arms/agents/models/shared/arms/glove_hardknuckle/glove_hardknuckle.glb"),
    }


def test_load_knife_and_clips(butterfly_knife_paths):
    """Verify that models and animation clips are parsed with valid tracks and durations."""
    animator = CSWeaponAnimator()
    animator.load_model(butterfly_knife_paths["model"])
    animator.load_clip("draw", butterfly_knife_paths["draw_clip"])
    animator.load_clip("inspect", butterfly_knife_paths["inspect_clip"])
    animator.load_clip("backstab", butterfly_knife_paths["backstab_clip"])

    assert len(animator.bones) > 0
    assert "draw" in animator.clips
    assert "inspect" in animator.clips
    assert "backstab" in animator.clips

    draw_clip = animator.clips["draw"]
    assert draw_clip.duration > 0.0
    assert len(draw_clip.channels) > 0

    inspect_clip = animator.clips["inspect"]
    assert inspect_clip.duration > 1.0  # Inspect loop is several seconds long
    assert len(inspect_clip.channels) > 0


def test_animator_state_machine_lifecycle(butterfly_knife_paths):
    """Verify state machine transitions: DRAWING -> IDLE -> INSPECTING -> ATTACK."""
    animator = CSWeaponAnimator()
    animator.load_model(butterfly_knife_paths["model"])
    animator.load_clip("draw", butterfly_knife_paths["draw_clip"])
    animator.load_clip("inspect", butterfly_knife_paths["inspect_clip"])
    animator.load_clip("backstab", butterfly_knife_paths["backstab_clip"])

    # 1. Starts in DRAWING state
    animator.trigger_draw()
    assert animator.state == CSWeaponState.DRAWING
    assert animator.current_time == 0.0

    # 2. Advance time past draw duration -> auto transitions to IDLE
    draw_dur = animator.clips["draw"].duration
    animator.tick(draw_dur + 0.1)
    assert animator.state == CSWeaponState.IDLE

    # 3. Trigger inspect (F key) -> transitions to INSPECTING
    animator.trigger_inspect()
    assert animator.state == CSWeaponState.INSPECTING

    # 4. Advance time within inspect loop -> remains in INSPECTING
    animator.tick(0.5)
    assert animator.state == CSWeaponState.INSPECTING
    assert animator.current_time > 0.0

    # 5. Trigger attack -> interrupts inspect immediately into ATTACK_HEAVY
    animator.trigger_attack_heavy()
    assert animator.state == CSWeaponState.ATTACK_HEAVY
    assert animator.current_time == 0.0


def test_bone_transforms_and_knife_flip(butterfly_knife_paths):
    """Verify that during inspect animation, bone matrices undergo non-trivial 3D rotation."""
    animator = CSWeaponAnimator()
    animator.load_model(butterfly_knife_paths["model"])
    animator.load_clip("inspect", butterfly_knife_paths["inspect_clip"])

    animator.trigger_inspect()
    pose_t0 = animator.evaluate_pose(0.0)
    pose_t1 = animator.evaluate_pose(1.0)

    assert len(pose_t0.bone_matrices) == len(animator.bones)
    assert len(pose_t1.bone_matrices) == len(animator.bones)

    # Assert all matrices are valid 4x4 affine transforms (finite, non-singular)
    for b_idx, mat in enumerate(pose_t0.bone_matrices):
        assert np.all(np.isfinite(mat)), f"Bone {b_idx} matrix has NaN/inf at t=0"
        det = np.linalg.det(mat[:3, :3])
        assert abs(det) > 1e-4, f"Bone {b_idx} matrix is singular at t=0: det={det}"

    # During butterfly inspect, the blade/handle bones must move significantly
    max_delta = 0.0
    for m0, m1 in zip(pose_t0.bone_matrices, pose_t1.bone_matrices):
        diff = np.max(np.abs(m1 - m0))
        if diff > max_delta:
            max_delta = diff

    assert max_delta > 0.1, f"Expected noticeable bone animation delta during inspect, got max_delta={max_delta}"
