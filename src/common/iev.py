"""
iev - IAP Vulkan Engine Python Bindings
Encapsulates all ctypes boilerplate and provides high-level helpers.
"""
import ctypes
import os
import glfw

# ── Vulkan Structures ──────────────────────────────────────────
class VkExtent2D(ctypes.Structure):
    _fields_ = [("width", ctypes.c_uint32), ("height", ctypes.c_uint32)]

class VkOffset2D(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int32), ("y", ctypes.c_int32)]

class VkRect2D(ctypes.Structure):
    _fields_ = [("offset", VkOffset2D), ("extent", VkExtent2D)]

class VkClearColorValue(ctypes.Union):
    _fields_ = [("float32", ctypes.c_float * 4)]

class VkClearValue(ctypes.Union):
    _fields_ = [("color", VkClearColorValue)]

class VkRenderPassBeginInfo(ctypes.Structure):
    _fields_ = [
        ("sType", ctypes.c_uint32), ("pNext", ctypes.c_void_p),
        ("renderPass", ctypes.c_void_p), ("framebuffer", ctypes.c_void_p),
        ("renderArea", VkRect2D), ("clearValueCount", ctypes.c_uint32),
        ("pClearValues", ctypes.POINTER(VkClearValue)),
    ]

# ── Internal: batch API declaration ────────────────────────────
def _decl(obj, name, args=None, ret=None):
    fn = getattr(obj, name)
    if args is not None: fn.argtypes = args
    if ret  is not None: fn.restype  = ret

P  = ctypes.c_void_p
U  = ctypes.c_uint32
B  = ctypes.c_bool
PP = ctypes.POINTER(U)
CS = ctypes.POINTER(ctypes.c_char_p)

def _setup_api(lib, vk):
    _decl(lib, "iev_device_context_create",         ret=P)
    _decl(lib, "iev_device_context_init_instance",  [P, U, CS], B)
    _decl(lib, "iev_device_context_init_device",    [P, P],     B)
    _decl(lib, "iev_device_context_get_instance",   [P],        P)
    _decl(lib, "iev_device_context_get_device",     [P],        P)
    _decl(lib, "iev_device_context_cleanup",        [P])
    _decl(lib, "iev_device_context_destroy",        [P])

    _decl(lib, "iev_window_context_create",              [P],          P)
    _decl(lib, "iev_window_context_init",                [P, P, U, U], B)
    _decl(lib, "iev_window_context_begin_frame",         [P, PP],      B)
    _decl(lib, "iev_window_context_end_frame",           [P, U])
    _decl(lib, "iev_window_context_get_current_frame",   [P],          U)
    _decl(lib, "iev_window_context_get_command_buffer",  [P, U],       P)
    _decl(lib, "iev_window_context_get_render_pass",     [P],          P)
    _decl(lib, "iev_window_context_get_framebuffer",     [P, U],       P)
    _decl(lib, "iev_window_context_get_swapchain_extent",[P],          VkExtent2D)
    _decl(lib, "iev_window_context_cleanup",             [P])
    _decl(lib, "iev_window_context_destroy",             [P])

    _decl(vk, "vkEndCommandBuffer",   [P])
    _decl(vk, "vkCmdBeginRenderPass", [P, ctypes.POINTER(VkRenderPassBeginInfo), U])
    _decl(vk, "vkCmdEndRenderPass",   [P])
    _decl(vk, "vkDeviceWaitIdle",     [P])
    _decl(vk, "vkDestroySurfaceKHR",  [P, P, P])

# ── Public: Engine Context ─────────────────────────────────────
class Engine:
    """High-level wrapper around the Vulkan engine C-API."""

    def __init__(self, lib_dir):
        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(lib_dir)
        self._lib = ctypes.CDLL(os.path.join(lib_dir, "iap_vulkan_engine.dll"))
        self._vk  = ctypes.CDLL("vulkan-1.dll")
        _setup_api(self._lib, self._vk)

        self._device_ctx = None
        self._window_ctx = None
        self._instance   = None
        self._surface    = None
        self._render_pass = None

    def init(self, glfw_window, width, height):
        """Initialize Vulkan device + window context."""
        lib = self._lib

        self._device_ctx = lib.iev_device_context_create()
        exts = glfw.get_required_instance_extensions()
        ext_array = (ctypes.c_char_p * len(exts))(*[e.encode('utf-8') for e in exts])
        lib.iev_device_context_init_instance(self._device_ctx, len(exts), ext_array)

        self._instance = lib.iev_device_context_get_instance(self._device_ctx)
        self._surface = ctypes.c_void_p()
        glfw.create_window_surface(self._instance, glfw_window, None, ctypes.byref(self._surface))
        lib.iev_device_context_init_device(self._device_ctx, self._surface)

        self._window_ctx = lib.iev_window_context_create(self._device_ctx)
        lib.iev_window_context_init(self._window_ctx, self._surface, width, height)
        self._render_pass = lib.iev_window_context_get_render_pass(self._window_ctx)

    def render_frame(self, clear_color=(0.1, 0.1, 0.15, 1.0)):
        """Execute one frame: begin → clear renderpass → end."""
        lib, vk = self._lib, self._vk
        idx = ctypes.c_uint32()
        if not lib.iev_window_context_begin_frame(self._window_ctx, ctypes.byref(idx)):
            return

        frame = lib.iev_window_context_get_current_frame(self._window_ctx)
        cmd   = lib.iev_window_context_get_command_buffer(self._window_ctx, frame)
        fb    = lib.iev_window_context_get_framebuffer(self._window_ctx, idx.value)
        ext   = lib.iev_window_context_get_swapchain_extent(self._window_ctx)

        clear = VkClearValue()
        clear.color.float32[:] = clear_color

        rp = VkRenderPassBeginInfo()
        rp.sType = 43
        rp.renderPass = self._render_pass
        rp.framebuffer = fb
        rp.renderArea.extent = ext
        rp.clearValueCount = 1
        rp.pClearValues = ctypes.pointer(clear)

        vk.vkCmdBeginRenderPass(cmd, ctypes.byref(rp), 0)
        vk.vkCmdEndRenderPass(cmd)
        vk.vkEndCommandBuffer(cmd)
        lib.iev_window_context_end_frame(self._window_ctx, idx.value)

    def shutdown(self):
        """Cleanup all Vulkan resources."""
        lib, vk = self._lib, self._vk
        vk.vkDeviceWaitIdle(lib.iev_device_context_get_device(self._device_ctx))
        lib.iev_window_context_cleanup(self._window_ctx)
        lib.iev_window_context_destroy(self._window_ctx)
        vk.vkDestroySurfaceKHR(self._instance, self._surface, None)
        lib.iev_device_context_cleanup(self._device_ctx)
        lib.iev_device_context_destroy(self._device_ctx)
