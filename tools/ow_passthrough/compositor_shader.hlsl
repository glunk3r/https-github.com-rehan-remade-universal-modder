// Overwatch inside Elden Ring: D3D12 Passthrough Compositor Shader
// Composites Guest RGBA + linear depth against Elden Ring reversed-Z depth buffer.

cbuffer PassthroughConstants : register(b0) {
    row_major float4x4 g_guest_view_proj;
    row_major float4x4 g_host_view_proj;
    float4 g_scene_params; // x: depth_constant (0.050067), y: rel_bias, z: abs_bias, w: enabled (1.0)
    float4 g_resolution;   // x: width, y: height, z: 1/width, w: 1/height
};

Texture2D<float>  t_host_depth  : register(t0); // Elden Ring reversed-Z depth
Texture2D<float4> t_guest_color : register(t1); // Guest RGBA color
Texture2D<float>  t_guest_depth : register(t2); // Guest linear depth (metres)
SamplerState      s_point_clamp : register(s0);

struct VSOutput {
    float4 pos : SV_POSITION;
    float2 uv  : TEXCOORD0;
};

// Fullscreen quad vertex shader
VSOutput VSMain(uint id : SV_VertexID) {
    VSOutput o;
    float2 uv = float2((id << 1) & 2, id & 2);
    o.pos = float4(uv * float2(2.0, -2.0) + float2(-1.0, 1.0), 0.0, 1.0);
    o.uv = uv;
    return o;
}

// Compositor pixel shader
float4 PSMain(VSOutput input) : SV_Target {
    if (g_scene_params.w < 0.5) {
        discard; // Compositor disabled
    }

    float4 guest_color = t_guest_color.Sample(s_point_clamp, input.uv);
    if (guest_color.a <= 0.01) {
        discard; // Background or transparent
    }

    float guest_z = t_guest_depth.Sample(s_point_clamp, input.uv);
    float host_d = t_host_depth.Sample(s_point_clamp, input.uv);

    // Convert Elden Ring reversed-Z to linear depth
    // Depth constant K ~ 0.050067 (derived from Dantelion engine projection)
    if (host_d > 0.0) {
        float host_z = g_scene_params.x / host_d;
        // Occlusion test: discard if host obstacle is closer than guest pixel
        if (guest_z > host_z * (1.0 + g_scene_params.y) + g_scene_params.z) {
            discard; // Occluded by Elden Ring world geometry (pillar, tree, terrain)
        }
    }

    return guest_color;
}
