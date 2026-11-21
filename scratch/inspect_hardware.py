import ctypes
import os
import platform
import psutil
import sys
import torch

def inspect_env():
    print("=== ENVIRONMENT & HARDWARE INSPECTION ===")
    print(f"OS: {platform.system()} {platform.release()} ({platform.version()})")
    print(f"Python: {sys.version}")
    print(f"PyTorch: {torch.__version__}")
    print(f"CUDA Available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        count = torch.cuda.device_count()
        print(f"CUDA Device Count: {count}")
        for i in range(count):
            name = torch.cuda.get_device_name(i)
            cap = torch.cuda.get_device_capability(i)
            props = torch.cuda.get_device_properties(i)
            total_vram_gb = props.total_memory / (1024**3)
            # Memory allocated/reserved
            alloc_mb = torch.cuda.memory_allocated(i) / (1024**2)
            res_mb = torch.cuda.memory_reserved(i) / (1024**2)
            
            # Using torch.cuda.mem_get_info()
            free_bytes, total_bytes = torch.cuda.mem_get_info(i)
            free_gb = free_bytes / (1024**3)
            total_gb = total_bytes / (1024**3)
            
            print(f"Device {i}: {name}")
            print(f"  Compute Capability: {cap[0]}.{cap[1]}")
            print(f"  Total VRAM: {total_gb:.3f} GB ({props.total_memory} bytes)")
            print(f"  Free VRAM: {free_gb:.3f} GB ({free_bytes} bytes)")
            print(f"  PyTorch Allocated: {alloc_mb:.2f} MB")
            print(f"  PyTorch Reserved: {res_mb:.2f} MB")
    else:
        print("CUDA is NOT available.")

    # System Memory via psutil
    vm = psutil.virtual_memory()
    print(f"\nSystem RAM:")
    print(f"  Total: {vm.total / (1024**3):.2f} GB")
    print(f"  Available: {vm.available / (1024**3):.2f} GB")
    print(f"  Used: {vm.used / (1024**3):.2f} GB ({vm.percent}%)")
    
    # CPU info
    print(f"\nCPU:")
    print(f"  Processor: {platform.processor()}")
    print(f"  Physical Cores: {psutil.cpu_count(logical=False)}")
    print(f"  Logical Cores: {psutil.cpu_count(logical=True)}")

if __name__ == "__main__":
    inspect_env()
