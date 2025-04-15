# ray_benchmark.py
from typing import Union, Any

import ray
import numpy as np
import time
import psutil
import os
import gc
import pandas as pd
from datetime import datetime
from typing import Union, Any, Dict


# Ray 클러스터에 연결
ray.init()

# 성능 측정 결과를 저장할 데이터프레임
results = []


# 메모리 사용량 측정 함수
def get_process_memory():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)  # MB 단위


# 이미지 처리 태스크 - 계산 집약적 작업
@ray.remote
def process_image(image, complexity=1):
    # 가우시안 블러 시뮬레이션
    kernel_size = 5 * complexity
    kernel = np.ones((kernel_size, kernel_size)) / (kernel_size * kernel_size)

    # 컨볼루션 연산 (계산 집약적)
    h, w = image.shape[:2]
    result = np.zeros_like(image, dtype=np.float32)

    # 패딩 처리
    padded = np.pad(image, ((kernel_size // 2, kernel_size // 2),
                            (kernel_size // 2, kernel_size // 2),
                            (0, 0)), mode='reflect')

    # 직접 컨볼루션 구현 (계산 부하 증가)
    for i in range(h):
        for j in range(w):
            for c in range(3):  # RGB 채널
                window = padded[i:i + kernel_size, j:j + kernel_size, c]
                result[i, j, c] = np.sum(window * kernel)

    # 추가 이미지 처리 작업
    result = np.clip(result * 1.2, 0, 255).astype(np.uint8)

    # 히스토그램 평활화 시뮬레이션
    for c in range(3):
        hist, bins = np.histogram(result[:, :, c].flatten(), 256, [0, 256])
        cdf = hist.cumsum()
        cdf_normalized = cdf * 255 / cdf[-1]
        result[:, :, c] = cdf_normalized[result[:, :, c]]

    return result


# 테스트 실행 함수
def run_ray_test(data_size_mb: int, num_tasks: int, complexity: int = 1) -> Dict[str, Union[int, float, str, Any]]:
    print(f"Running Ray test: {data_size_mb}MB, {num_tasks} tasks, complexity {complexity}")

    # 이미지 크기 계산 (각 이미지는 약 3MB)
    img_size = int(np.sqrt((data_size_mb * 1024 * 1024) / (3 * num_tasks * 4)))

    # 테스트 이미지 생성
    images = [np.random.randint(0, 256, (img_size, img_size, 3), dtype=np.uint8)
              for _ in range(num_tasks)]

    # 메모리 측정 시작
    start_mem = get_process_memory()

    # 시간 측정 시작
    start_time = time.time()

    # Ray 태스크 제출
    futures = [process_image.remote(img, complexity) for img in images]

    # 결과 수집
    results = ray.get(futures)

    # 시간 측정 종료
    end_time = time.time()

    # 메모리 측정 종료
    end_mem = get_process_memory()

    # 결과 정리
    execution_time = end_time - start_time
    memory_used = end_mem - start_mem

    print(f"Execution time: {execution_time:.2f} seconds")
    print(f"Memory used: {memory_used:.2f} MB")

    return {
        'framework': 'Ray',
        'data_size_mb': data_size_mb,
        'num_tasks': num_tasks,
        'complexity': complexity,
        'execution_time': execution_time,
        'memory_used': memory_used
    }


# 다양한 조건으로 테스트 실행
test_configs = [
    # 데이터 크기 테스트
    {'data_size_mb': 100, 'num_tasks': 10, 'complexity': 1},
    {'data_size_mb': 100, 'num_tasks': 30, 'complexity': 1},
    {'data_size_mb': 100, 'num_tasks': 50, 'complexity': 1},

    # 태스크 수 테스트
    # {'data_size_mb': 500, 'num_tasks': 20, 'complexity': 1},
    # {'data_size_mb': 500, 'num_tasks': 50, 'complexity': 1},
    # {'data_size_mb': 500, 'num_tasks': 100, 'complexity': 1},

    # 복잡도 테스트
    # {'data_size_mb': 500, 'num_tasks': 20, 'complexity': 2},
    # {'data_size_mb': 500, 'num_tasks': 20, 'complexity': 3},
]

if __name__ == '__main__':
    # 모든 테스트 실행
    for config in test_configs:
        # 가비지 컬렉션 실행으로 이전 테스트의 영향 최소화
        gc.collect()
        time.sleep(2)

        # 테스트 실행
        result = run_ray_test(**config)
        results.append(result)

    # 결과를 CSV로 저장
    df = pd.DataFrame(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    df.to_csv(f"ray_benchmark_results_{timestamp}.csv", index=False)

    print("Ray benchmark completed!")
    ray.shutdown()
