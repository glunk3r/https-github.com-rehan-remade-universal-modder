/**
 * Overwatch Passthrough ReShade 6.x Add-on for Elden Ring.
 *
 * Connects to Windows named shared memory "Local\OWPassthroughFrame",
 * retrieves 60 FPS guest color and linear depth buffers via Seqlock,
 * and dynamically binds them to ReShade semantics OWWORLD and OWDEPTH.
 */
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <cstdint>
#include <cstring>
#include <atomic>
#include <initializer_list>

#include "reshade.hpp"

using namespace reshade::api;

namespace
{
    constexpr const wchar_t *kMappingName = L"Local\\OWPassthroughFrame";
    constexpr uint32_t kMagic = 0x4F575053; // "OWPS"
    constexpr size_t kHeaderSize = 4096;
    constexpr size_t kSlotHeaderSize = 64;

#pragma pack(push, 1)
    struct OWHeader
    {
        uint32_t magic;
        uint32_t version;
        uint32_t width;
        uint32_t height;
        int32_t active_slot;
        int32_t slot_count;
        int64_t stride;
        int64_t published_seq;
    };

    struct OWSlot
    {
        int64_t seqlock;
        int64_t timestamp_us;
        float cam_x, cam_y, cam_z;
        float yaw, pitch;
        uint32_t color_offset;
        uint32_t depth_offset;
    };
#pragma pack(pop)

    struct TextureLayer
    {
        resource tex = {0};
        resource_view srv = {0};
    };

    HANDLE g_mapping = nullptr;
    const uint8_t *g_view = nullptr;
    int64_t g_lastPublish = -1;
    DWORD g_nextOpenAttempt = 0;

    TextureLayer g_world;
    TextureLayer g_depth;
    uint32_t g_width = 0;
    uint32_t g_height = 0;

    bool open_mapping()
    {
        if (g_view != nullptr)
            return true;

        if (GetTickCount() < g_nextOpenAttempt)
            return false;
        g_nextOpenAttempt = GetTickCount() + 1000;

        g_mapping = OpenFileMappingW(FILE_MAP_READ, FALSE, kMappingName);
        if (g_mapping == nullptr)
            return false;

        const auto *header_raw = static_cast<const uint8_t *>(MapViewOfFile(g_mapping, FILE_MAP_READ, 0, 0, kHeaderSize));
        if (header_raw == nullptr)
        {
            CloseHandle(g_mapping);
            g_mapping = nullptr;
            return false;
        }

        const auto *header = reinterpret_cast<const OWHeader *>(header_raw);
        if (header->magic != kMagic)
        {
            UnmapViewOfFile(header_raw);
            CloseHandle(g_mapping);
            g_mapping = nullptr;
            return false;
        }

        int32_t slots = header->slot_count;
        int64_t stride = header->stride;
        UnmapViewOfFile(header_raw);

        size_t total_size = kHeaderSize + static_cast<size_t>(stride * slots);
        g_view = static_cast<const uint8_t *>(MapViewOfFile(g_mapping, FILE_MAP_READ, 0, 0, total_size));
        if (g_view == nullptr)
        {
            CloseHandle(g_mapping);
            g_mapping = nullptr;
            return false;
        }

        reshade::log::message(reshade::log::level::info, "OWPassthrough: Connected to Local\\OWPassthroughFrame");
        return true;
    }

    void destroy_layers(device *dev)
    {
        for (TextureLayer *layer : {&g_world, &g_depth})
        {
            if (layer->srv.handle != 0)
                dev->destroy_resource_view(layer->srv);
            if (layer->tex.handle != 0)
                dev->destroy_resource(layer->tex);
            *layer = TextureLayer();
        }
        g_width = 0;
        g_height = 0;
    }

    bool create_layer(device *dev, TextureLayer &layer, uint32_t w, uint32_t h, format fmt)
    {
        if (!dev->create_resource(
                resource_desc(w, h, 1, 1, fmt, 1, memory_heap::default_, resource_usage::shader_resource | resource_usage::copy_dest),
                nullptr, resource_usage::shader_resource, &layer.tex))
            return false;
        return dev->create_resource_view(layer.tex, resource_usage::shader_resource, resource_view_desc(fmt), &layer.srv);
    }

    void bind(effect_runtime *runtime)
    {
        runtime->update_texture_bindings("OWWORLD", g_world.srv, g_world.srv);
        runtime->update_texture_bindings("OWDEPTH", g_depth.srv, g_depth.srv);
    }

    void upload(effect_runtime *runtime)
    {
        if (!open_mapping())
            return;

        const auto *header = reinterpret_cast<const OWHeader *>(g_view);
        if (header->magic != kMagic)
            return;

        int64_t published = header->published_seq;
        if (published == g_lastPublish)
            return;

        int32_t active_slot = header->active_slot;
        if (active_slot < 0 || active_slot >= header->slot_count)
            return;

        size_t slot_offset = kHeaderSize + static_cast<size_t>(active_slot * header->stride);
        const auto *slot = reinterpret_cast<const OWSlot *>(g_view + slot_offset);

        // Seqlock check 1: reject if mid-write
        int64_t seq = slot->seqlock;
        if (seq & 1)
            return;

        uint32_t w = header->width;
        uint32_t h = header->height;
        if (w == 0 || h == 0)
            return;

        device *dev = runtime->get_device();
        if (w != g_width || h != g_height)
        {
            destroy_layers(dev);
            if (!create_layer(dev, g_world, w, h, format::r8g8b8a8_unorm) ||
                !create_layer(dev, g_depth, w, h, format::r32_float))
            {
                destroy_layers(dev);
                return;
            }
            g_width = w;
            g_height = h;
            bind(runtime);
        }

        const uint8_t *slot_base = g_view + slot_offset;
        const uint8_t *color_ptr = slot_base + slot->color_offset;
        const uint8_t *depth_ptr = slot_base + slot->depth_offset;

        subresource_data data;
        data.row_pitch = w * 4;
        data.slice_pitch = w * h * 4;

        data.data = const_cast<uint8_t *>(color_ptr);
        dev->update_texture_region(data, g_world.tex, 0);

        data.data = const_cast<uint8_t *>(depth_ptr);
        dev->update_texture_region(data, g_depth.tex, 0);

        // Seqlock check 2: verify slot wasn't overwritten during copy
        if (slot->seqlock != seq)
            return;

        g_lastPublish = published;
    }

    void on_begin_effects(effect_runtime *runtime, command_list *, resource_view, resource_view)
    {
        upload(runtime);
    }

    void on_reloaded_effects(effect_runtime *runtime)
    {
        if (g_width != 0)
            bind(runtime);
    }

    void on_destroy_effect_runtime(effect_runtime *runtime)
    {
        destroy_layers(runtime->get_device());
    }
}

extern "C" __declspec(dllexport) const char *NAME = "Overwatch Passthrough Compositor";
extern "C" __declspec(dllexport) const char *DESCRIPTION = "Reads Overwatch guest color and depth buffers from shared memory and binds to OWWorldTex and OWDepthTex.";

static bool register_all_events(void *addon_module, void *reshade_module = nullptr)
{
    if (!reshade::register_addon(addon_module, reshade_module))
        return false;
    reshade::register_event<reshade::addon_event::reshade_begin_effects>(on_begin_effects);
    reshade::register_event<reshade::addon_event::reshade_reloaded_effects>(on_reloaded_effects);
    reshade::register_event<reshade::addon_event::destroy_effect_runtime>(on_destroy_effect_runtime);
    return true;
}

extern "C" __declspec(dllexport) bool AddonInit(HMODULE addon_module, HMODULE reshade_module)
{
    reshade::internal::get_current_module_handle(addon_module);
    reshade::internal::get_reshade_module_handle(reshade_module);
    return register_all_events(addon_module, reshade_module);
}

extern "C" __declspec(dllexport) void AddonUninit(HMODULE addon_module, HMODULE reshade_module)
{
    reshade::unregister_addon(addon_module, reshade_module);
}

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID)
{
    if (fdwReason == DLL_PROCESS_ATTACH)
    {
        reshade::internal::get_current_module_handle(hinstDLL);
    }
    return TRUE;
}
