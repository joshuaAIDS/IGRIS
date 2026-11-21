import os
import sys
import json
import subprocess
import platform
import shutil
import ctypes

info = {}

# CPU details
info["cpu_model"] = platform.processor()
info["machine"] = platform.machine()
info["cpu_count_logical"] = os.cpu_count()

# Run wmic or powershell for CPU physical cores
try:
    cmd = 'powershell -Command "Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors | ConvertTo-Json"'
    res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    proc_data = json.loads(res.stdout)
    info["cpu_name"] = proc_data.get("Name")
    info["cpu_physical_cores"] = proc_data.get("NumberOfCores")
    info["cpu_logical_cores"] = proc_data.get("NumberOfLogicalProcessors")
except Exception as e:
    info["cpu_query_error"] = str(e)

# Memory
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

info["ram_total_bytes"] = stat.ullTotalPhys
info["ram_total_gib"] = round(stat.ullTotalPhys / (1024**3), 2)
info["ram_avail_bytes"] = stat.ullAvailPhys
info["ram_avail_gib"] = round(stat.ullAvailPhys / (1024**3), 2)
info["ram_load_percent"] = stat.dwMemoryLoad

# Disks and Volume Info
try:
    cmd_vol = 'powershell -Command "Get-Volume | Select-Object DriveLetter, FileSystem, FileSystemLabel, Size, SizeRemaining | ConvertTo-Json"'
    res_vol = subprocess.run(cmd_vol, capture_output=True, text=True, shell=True)
    vol_data = json.loads(res_vol.stdout)
    info["volumes"] = vol_data
except Exception as e:
    info["vol_query_error"] = str(e)

# GPU
try:
    import torch
    info["pytorch_version"] = torch.__version__
    info["cuda_available"] = torch.cuda.is_available()
    if torch.cuda.is_available():
        info["cuda_version"] = torch.version.cuda
        info["cudnn_version"] = torch.backends.cudnn.version()
        info["gpu_name"] = torch.cuda.get_device_name(0)
        props = torch.cuda.get_device_properties(0)
        info["gpu_vram_total_bytes"] = props.total_memory
        info["gpu_vram_total_gib"] = round(props.total_memory / (1024**3), 2)
        info["gpu_compute_capability"] = f"{props.major}.{props.minor}"
        info["gpu_sm_count"] = props.multi_processor_count
        info["bf16_supported"] = torch.cuda.is_bf16_supported()
except Exception as e:
    info["gpu_query_error"] = str(e)

print(json.dumps(info, indent=2))
with open(r"C:\IGRIS\scratch\detailed_hardware.json", "w", encoding="utf-8") as f:
    json.dump(info, f, indent=2)
