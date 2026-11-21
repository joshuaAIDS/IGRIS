import json
import os
import platform
import subprocess
import psutil
import torch

def probe_hardware():
    results = {}
    
    # 1. NVIDIA-SMI / NVML Telemetry
    try:
        smi_query = subprocess.run(
            ['nvidia-smi', '--query-gpu=name,memory.total,memory.free,memory.used,driver_version', '--format=csv,noheader,nounits'],
            capture_output=True, text=True, check=True
        )
        parts = [p.strip() for p in smi_query.stdout.strip().split(',')]
        results['nvidia_smi'] = {
            'gpu_name': parts[0],
            'total_vram_mib': float(parts[1]),
            'total_vram_gb': round(float(parts[1]) / 1024, 2),
            'free_vram_mib': float(parts[2]),
            'free_vram_gb': round(float(parts[2]) / 1024, 2),
            'used_vram_mib': float(parts[3]),
            'used_vram_gb': round(float(parts[3]) / 1024, 2),
            'driver_version': parts[4],
        }
    except Exception as e:
        results['nvidia_smi'] = {'error': str(e)}

    # 2. PyTorch CUDA Telemetry
    results['pytorch_cuda'] = {
        'version': torch.__version__,
        'cuda_available': torch.cuda.is_available(),
    }
    if torch.cuda.is_available():
        gpu_idx = 0
        props = torch.cuda.get_device_properties(gpu_idx)
        free_bytes, total_bytes = torch.cuda.mem_get_info(gpu_idx)
        results['pytorch_cuda'].update({
            'device_name': torch.cuda.get_device_name(gpu_idx),
            'device_properties': {
                'name': props.name,
                'major': props.major,
                'minor': props.minor,
                'total_memory_bytes': props.total_memory,
                'total_memory_mib': round(props.total_memory / (1024**2), 2),
                'total_memory_gb': round(props.total_memory / (1024**3), 2),
                'multi_processor_count': props.multi_processor_count,
            },
            'mem_get_info': {
                'free_bytes': free_bytes,
                'free_mib': round(free_bytes / (1024**2), 2),
                'free_gb': round(free_bytes / (1024**3), 2),
                'total_bytes': total_bytes,
                'total_mib': round(total_bytes / (1024**2), 2),
                'total_gb': round(total_bytes / (1024**3), 2),
            },
            'memory_allocated_bytes': torch.cuda.memory_allocated(gpu_idx),
            'memory_reserved_bytes': torch.cuda.memory_reserved(gpu_idx),
            'max_memory_allocated_bytes': torch.cuda.max_memory_allocated(gpu_idx),
            'max_memory_reserved_bytes': torch.cuda.max_memory_reserved(gpu_idx),
        })

    # 3. System RAM Telemetry
    vm = psutil.virtual_memory()
    results['system_ram'] = {
        'total_bytes': vm.total,
        'total_gb': round(vm.total / (1024**3), 2),
        'available_bytes': vm.available,
        'available_gb': round(vm.available / (1024**3), 2),
        'used_bytes': vm.total - vm.available,
        'used_gb': round((vm.total - vm.available) / (1024**3), 2),
        'percent_used': vm.percent,
    }

    # 4. OS & CPU Telemetry
    results['os_cpu'] = {
        'platform': platform.platform(),
        'processor': platform.processor(),
        'cpu_count_logical': os.cpu_count(),
    }

    print(json.dumps(results, indent=2))
    return results

if __name__ == '__main__':
    probe_hardware()
