// OWPassthrough.fx: Composites Overwatch Guest character into Elden Ring via ReShade.
// Tested against Elden Ring Dantelion engine (D3D12, reversed-Z depth).

#include "ReShade.fxh"

// Textures bound from shared memory by the compositor
texture OWWorldTex : OWWORLD;
texture OWDepthTex : OWDEPTH;

sampler sOWWorld { Texture = OWWorldTex; AddressU = CLAMP; AddressV = CLAMP; };
sampler sOWDepth { Texture = OWDepthTex; MinFilter = POINT; MagFilter = POINT; AddressU = CLAMP; AddressV = CLAMP; };

uniform bool OwActive <
    ui_label = "Enable Overwatch Character Passthrough";
    ui_tooltip = "Composites the rendered Overwatch hero over Elden Ring.";
> = true;

uniform bool HostReversedZ <
    ui_label = "Elden Ring Reversed-Z Depth";
    ui_tooltip = "FromSoftware Dantelion uses reversed-Z (1.0 near, 0.0 far).";
> = true;

uniform float DepthConstant <
    ui_type = "drag";
    ui_min = 0.01; ui_max = 0.20; ui_step = 0.001;
    ui_label = "Depth Constant (K)";
    ui_tooltip = "Camera depth constant derived from Elden Ring projection (0.050067).";
> = 0.050067;

uniform float DepthBias <
    ui_type = "drag";
    ui_min = 0.0; ui_max = 1.0; ui_step = 0.01;
    ui_label = "Depth Bias (metres)";
    ui_tooltip = "Allowance before character is considered occluded by scenery.";
> = 0.05;

uniform float LightMatch <
    ui_type = "drag";
    ui_min = 0.0; ui_max = 1.0; ui_step = 0.01;
    ui_label = "Match Elden Ring Lighting";
    ui_tooltip = "Tints character by blurred surrounding Elden Ring scene luminance.";
> = 0.70;

float4 PS_OWComposite(float4 pos : SV_Position, float2 texcoord : TEXCOORD) : SV_Target {
    float4 host_color = tex2D(ReShade::sBackBuffer, texcoord);

    if (!OwActive) {
        return host_color;
    }

    float4 ow_color = tex2D(sOWWorld, texcoord);
    if (ow_color.a <= 0.01) {
        return host_color; // Transparent background
    }

    float ow_depth_m = tex2D(sOWDepth, texcoord).r;
    float host_raw_depth = ReShade::GetLinearizedDepth(texcoord);

    // In Elden Ring reversed-Z: host_z (metres) ~ DepthConstant / raw_depth
    float host_depth_m = 10000.0;
    if (host_raw_depth > 0.0001) {
        host_depth_m = DepthConstant / host_raw_depth;
    }

    // Occlusion check
    if (ow_depth_m > host_depth_m + DepthBias) {
        return host_color; // Occluded by Elden Ring environment (trees, stones, walls)
    }

    // Environmental lighting approximation: mix ambient luminance
    float3 lum = dot(host_color.rgb, float3(0.299, 0.587, 0.114));
    float3 final_color = lerp(ow_color.rgb, ow_color.rgb * (lum * 1.5), LightMatch);

    return float4(lerp(host_color.rgb, final_color, ow_color.a), 1.0);
}

technique OWPassthrough {
    pass P0 {
        VertexShader = PostProcessVS;
        PixelShader = PS_OWComposite;
    }
}
