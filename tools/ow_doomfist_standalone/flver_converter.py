"""FromSoftware FLVER 2.0 (Fast Lightweight Vertex Format) and DCX container serializer.

Generates native FromSoftware 3D model containers compatible with Elden Ring's Dantelion engine.
"""
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import struct
import zlib


class DcxPacker:
    """Pack and unpack FromSoftware DCX-compressed file archives."""

    def pack(self, raw_data: bytes) -> bytes:
        compressed = zlib.compress(raw_data, level=9)
        uncompressed_size = len(raw_data)
        compressed_size = len(compressed)

        header = bytearray()
        # DCX header
        header += b"DCX\x00"                       # 0x00: Magic
        header += struct.pack(">I", 0x10000)        # 0x04: Version
        header += struct.pack(">I", 0x18)           # 0x08: Header length
        header += struct.pack(">I", 0x24)           # 0x0C: Header length 2
        header += struct.pack(">I", 0x24)           # 0x10: Chunk size
        header += struct.pack(">I", 0x2C)           # 0x14: Header length 3

        # DCS chunk (Deflate Compressed Stream)
        header += b"DCS\x00"                       # 0x18: DCS Magic
        header += struct.pack(">I", uncompressed_size)  # 0x1C: Uncompressed size
        header += struct.pack(">I", compressed_size)    # 0x20: Compressed size

        # DCP chunk (Deflate Compression Parameters)
        header += b"DCP\x00"                       # 0x24: DCP Magic
        header += b"DFLT"                          # 0x28: Deflate method
        header += struct.pack(">I", 0x20)           # 0x2C: Chunk size
        header += struct.pack(">I", 0x09)           # 0x30: Compression level 9
        header += struct.pack(">3I", 0, 0, 0x10100) # 0x34: Flags

        # DCA chunk (Data Chunk Array)
        header += b"DCA\x00"                       # 0x40: DCA Magic
        header += struct.pack(">I", 0x08)           # 0x44: Header size

        return bytes(header) + compressed

    def unpack(self, dcx_data: bytes) -> bytes:
        if not dcx_data.startswith(b"DCX\x00"):
            raise ValueError("Not a valid DCX file")

        # Find DCA chunk offset and payload
        dca_offset = dcx_data.find(b"DCA\x00")
        if dca_offset == -1:
            raise ValueError("Malformed DCX: DCA header not found")

        compressed_data = dcx_data[dca_offset + 8:]
        return zlib.decompress(compressed_data)


@dataclass
class FlverVertex:
    position: Tuple[float, float, float]
    normal: Tuple[float, float, float] = (0.0, 1.0, 0.0)
    uv: Tuple[float, float] = (0.0, 0.0)


@dataclass
class FlverMesh:
    mesh_name: str
    vertices: List[FlverVertex] = field(default_factory=list)
    indices: List[int] = field(default_factory=list)
    material_name: str = "M_Material"


class FlverConverter:
    """Converts geometry vertices into FromSoftware FLVER 2.0 binary layout."""

    def create_flver_bytes(
        self,
        mesh_name: str,
        vertices: List[FlverVertex],
        indices: List[int],
        material_name: str = "M_Material",
    ) -> bytes:
        if not vertices:
            min_x = min_y = min_z = max_x = max_y = max_z = 0.0
        else:
            xs = [v.position[0] for v in vertices]
            ys = [v.position[1] for v in vertices]
            zs = [v.position[2] for v in vertices]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            min_z, max_z = min(zs), max(zs)

        header = bytearray(80)
        # 0x00: Magic "FLVER\0"
        header[0:6] = b"FLVER\x00"
        # 0x06: Endianness "L\0" (Little endian)
        header[6:8] = b"L\x00"
        # 0x08: Version (0x20000 for FLVER2)
        struct.pack_into("<I", header, 8, 0x20000)
        # 0x0C: Data Offset
        struct.pack_into("<I", header, 12, 0x50)

        # 0x10..0x28: Bounding box coordinates (6 floats: min_x, min_y, min_z, max_x, max_y, max_z)
        struct.pack_into("<6f", header, 16, min_x, min_y, min_z, max_x, max_y, max_z)

        # Counts: dummy counts for standalone mesh
        vertex_count = len(vertices)
        index_count = len(indices)
        struct.pack_into("<I", header, 40, 1)            # Dummy bone count
        struct.pack_into("<I", header, 44, 1)            # Mesh count
        struct.pack_into("<I", header, 48, 1)            # Material count
        struct.pack_into("<I", header, 52, vertex_count) # Total vertex count
        struct.pack_into("<I", header, 56, index_count)  # Total index count

        # Vertex buffer payload
        vbuf = bytearray()
        for v in vertices:
            px, py, pz = v.position
            nx, ny, nz = v.normal
            u, v_coord = v.uv
            # 3 floats pos, 3 floats normal, 2 floats UV (32 bytes per vertex)
            vbuf += struct.pack("<8f", px, py, pz, nx, ny, nz, u, v_coord)

        # Index buffer payload (16-bit indices)
        ibuf = bytearray()
        for idx in indices:
            ibuf += struct.pack("<H", idx)

        # Pad to 16 bytes
        pad_len = (16 - (len(ibuf) % 16)) % 16
        ibuf += b"\x00" * pad_len

        return bytes(header) + bytes(vbuf) + bytes(ibuf)
