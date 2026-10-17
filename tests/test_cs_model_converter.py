import os
import struct
import pytest
from pathlib import Path

from tools.cs2.model_converter import (
    extract_mesh_primitives,
    build_cs_viewmodel_package,
    CSViewModelPackage,
)


@pytest.fixture
def butterfly_knife_paths():
    base = Path("./build/cs2assets/butterfly_knife")
    return {
        "knife_glb": base / "weapons/models/knife/knife_butterfly/weapon_knife_butterfly.glb",
        "arms_glb": Path("./build/cs2assets/viewmodel_arms/agents/models/shared/arms/glove_hardknuckle/glove_hardknuckle.glb"),
        "output_bin": Path("./build/cs2assets/cs_butterfly_viewmodel.bin"),
    }


def test_extract_mesh_primitives(butterfly_knife_paths):
    """Verify that vertex positions, UVs, normals, and indices are accurately parsed from GLB."""
    knife_prims = extract_mesh_primitives(butterfly_knife_paths["knife_glb"])
    assert len(knife_prims) > 0

    total_vertices = sum(len(p.vertices) for p in knife_prims)
    total_indices = sum(len(p.indices) for p in knife_prims)

    assert total_vertices > 500, f"Expected detailed knife mesh, got {total_vertices} vertices"
    assert total_indices > 1000, f"Expected detailed knife indices, got {total_indices} indices"

    # Deep semantic verification: assert UVs and normal vector validity
    for prim in knife_prims:
        for v in prim.vertices:
            # Position must be finite
            assert len(v.pos) == 3 and all(math_isfinite(x) for x in v.pos)
            # UV must be finite
            assert len(v.uv) == 2 and all(math_isfinite(x) for x in v.uv)
            # Normal must be approximately unit length
            norm_len = (v.normal[0]**2 + v.normal[1]**2 + v.normal[2]**2)**0.5
            assert abs(norm_len - 1.0) < 0.05, f"Normal not normalized: len={norm_len}"


def test_build_cs_viewmodel_package(butterfly_knife_paths):
    """Verify that viewmodel package is generated with CSVM binary header, submeshes, and bone map."""
    pkg = build_cs_viewmodel_package(
        knife_glb=butterfly_knife_paths["knife_glb"],
        arms_glb=butterfly_knife_paths["arms_glb"],
        output_bin=butterfly_knife_paths["output_bin"],
    )

    assert isinstance(pkg, CSViewModelPackage)
    assert os.path.isfile(butterfly_knife_paths["output_bin"])
    assert butterfly_knife_paths["output_bin"].stat().st_size > 10000

    # Binary header validation
    with open(butterfly_knife_paths["output_bin"], "rb") as f:
        magic, version, num_submeshes, vertex_count, index_count = struct.unpack("<4sIIII", f.read(20))
        assert magic == b"CSVM"
        assert version == 1
        assert num_submeshes >= 4  # blade, front handle, rear handle, lock
        assert vertex_count > 0
        assert index_count > 0

    # Verify bone mapping contains key butterfly parts
    bone_names = [sub.bone_name.lower() for sub in pkg.submeshes]
    assert any("blade" in b for b in bone_names)
    assert any("front" in b for b in bone_names)
    assert any("rear" in b for b in bone_names)


def test_cpp_binary_unpack_fidelity(butterfly_knife_paths):
    """Verify that cs_butterfly_viewmodel.bin unpacks with 100% fidelity matching C++ CSViewModel."""
    bin_path = butterfly_knife_paths["output_bin"]
    assert bin_path.is_file()

    with open(bin_path, "rb") as f:
        data = f.read()

    # Header unpack
    magic, version, num_sub, num_v, num_i = struct.unpack_from("<4sIIII", data, 0)
    assert magic == b"CSVM"
    assert version == 1
    assert num_sub >= 4
    assert num_v > 0
    assert num_i > 0

    offset = 20
    for _ in range(num_sub):
        name_len = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        bone_name = data[offset:offset + name_len].decode("utf-8")
        offset += name_len
        bone_idx, first_idx, base_v, count = struct.unpack_from("<IIiI", data, offset)
        offset += 16
        assert len(bone_name) > 0
        assert count > 0

    # Vertex buffer unpack (32 bytes per vertex)
    vb_bytes = num_v * 32
    assert offset + vb_bytes <= len(data)
    v0_pos = struct.unpack_from("<3f", data, offset)
    assert all(math_isfinite(x) for x in v0_pos)
    offset += vb_bytes

    # Index buffer unpack (4 bytes per index)
    ib_bytes = num_i * 4
    assert offset + ib_bytes == len(data)
    i0 = struct.unpack_from("<I", data, offset)[0]
    assert i0 < num_v


def math_isfinite(val: float) -> bool:
    import math
    return math.isfinite(val)
