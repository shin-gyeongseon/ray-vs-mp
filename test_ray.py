import ray

# Ray 클러스터 초기화
ray.init(address="ray://localhost:10001")  # 클러스터 주소에 맞게 수정

# 간단한 출력 작업 정의
@ray.remote(num_cpus=1)
def simple_task(message):
    return f"Task executed with message: {message}"

# 테스트 실행
if __name__ == "__main__":
    # 메시지 리스트 생성
    messages = [f"Hello from task {i}" for i in range(5)]

    # Ray 태스크 제출
    futures = [simple_task.remote(msg) for msg in messages]

    # 결과 수집 및 출력
    results = ray.get(futures)
    for result in results:
        print(result)

    # Ray 종료
    ray.shutdown()
