import numpy as np
import time
import psutil
import os
import gc
import pandas as pd
from datetime import datetime
from typing import Union, Any, Dict
from multiprocessing import Pool, cpu_count

results = []

def get_process_memory():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def process_image(args):
    image, complexity = args
    kernel_size = 5 * complexity
    kernel = np.ones((kernel_size, kernel_size)) / (kernel_size * kernel_size)
    h, w = image.shape[:2]
    result = np.zeros_like(image, dtype=np.float32)
    padded = np.pad(image, ((kernel_size // 2, kernel_size // 2),
                            (kernel_size // 2, kernel_size // 2),
                            (0, 0)), mode='reflect')
    for i in range(h):
        for j in range(w):
            for c in range(3):
                window = padded[i:i + kernel_size, j:j + kernel_size, c]
                result[i, j, c] = np.sum(window * kernel)
    result = np.clip(result * 1.2, 0, 255).astype(np.uint8)
    for c in range(3):
        hist, bins = np.histogram(result[:, :, c].flatten(), 256, [0, 256])
        cdf = hist.cumsum()
        cdf_normalized = cdf * 255 / cdf[-1]
        result[:, :, c] = cdf_normalized[result[:, :, c]]
    return result

def run_mp_test(data_size_mb: int, num_tasks: int, complexity: int = 1) -> Dict[str, Union[int, float, str, Any]]:
    print(f"Running Multiprocessing test: {data_size_mb}MB, {num_tasks} tasks, complexity {complexity}")
    img_size = int(np.sqrt((data_size_mb * 1024 * 1024) / (3 * num_tasks * 4)))
    images = [np.random.randint(0, 256, (img_size, img_size, 3), dtype=np.uint8) for _ in range(num_tasks)]
    start_mem = get_process_memory()
    start_time = time.time()
    with Pool(processes=num_tasks) as pool:
        results = pool.map(process_image, [(img, complexity) for img in images])
    end_time = time.time()
    end_mem = get_process_memory()
    execution_time = end_time - start_time
    memory_used = end_mem - start_mem
    print(f"Execution time: {execution_time:.2f} seconds")
    print(f"Memory used: {memory_used:.2f} MB")
    return {
        'framework': 'Multiprocessing',
        'data_size_mb': data_size_mb,
        'num_tasks': num_tasks,
        'complexity': complexity,
        'execution_time': execution_time,
        'memory_used': memory_used
    }

test_configs = [
    {'data_size_mb': 100, 'num_tasks': 10, 'complexity': 1},
    {'data_size_mb': 100, 'num_tasks': 30, 'complexity': 1},
    {'data_size_mb': 100, 'num_tasks': 50, 'complexity': 1},
]

if __name__ == '__main__':
    for config in test_configs:
        gc.collect()
        time.sleep(2)
        result = run_mp_test(**config)
        results.append(result)
    df = pd.DataFrame(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    df.to_csv(f"mp_benchmark_results_{timestamp}.csv", index=False)
    print("Multiprocessing benchmark completed!")