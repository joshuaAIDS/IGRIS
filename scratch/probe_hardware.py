import torch
import shutil
import platform
import json
import ctypes

data = {}
data["os"] = f"{platform.system()} {platform.release()} ({platform.version()})"
data["machine"] = platform.machine()
data["processor"] = platform.processor()
data["python_version"] = platform.python_version()
data["torch_version"] = torch.__version__
data["cuda_available"] = torch.cuda.is_available()

if torch.cuda.is_available():
    data["cuda_version"] = torch.version.cuda
    data["cudnn_version"] = torch.backends.cudnn.version() if torch.backends.cudnn.is_available() else None
    data["device_count"] = torch.cuda.device_count()
    data["device_name"] = torch.cuda.get_device_name(0)
    props = torch.cuda.get_device_properties(0)
    data["device_total_memory_bytes"] = props.total_memory
    data["device_total_memory_gib"] = round(props.total_memory / (1024**3), 2)
    data["compute_capability"] = f"{props.major}.{props.minor}"
    data["multi_processor_count"] = props.multi_processor_count
    # Check bf16 support
    data["bf16_supported"] = torch.cuda.is_bf16_supported()
else:
    data["cuda_version"] = None
    data["device_name"] = None

# Get Windows memory via ctypes
class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]

stat = MEMORYSTATUSEX()
stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))

data["ram_total_bytes"] = stat.ullTotalPhys
data["ram_total_gib"] = round(stat.ullTotalPhys / (1024**3), 2)
data["ram_available_bytes"] = stat.ullAvailPhys
data["ram_available_gib"] = round(stat.ullAvailPhys / (1024**3), 2)
data["memory_load_percent"] = stat.dwMemoryLoad

disks = {}
for p in ["C:\\", "D:\\", "E:\\"]:
    try:
        du = shutil.disk_usage(p)
        disks[p] = {
            "total_bytes": du.total,
            "total_gib": round(du.total / (1024**3), 2),
            "free_bytes": du.free,
            "free_gib": round(du.free / (1024**3), 2),
            "used_bytes": du.used,
            "used_gib": round(du.used / (1024**3), 2)
        }
    except Exception:
        pass
data["disks"] = disks

print(json.dumps(data, indent=2))
with open(r"C:\IGRIS\scratch\hardware_probe.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
