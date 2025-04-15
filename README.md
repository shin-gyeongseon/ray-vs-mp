# ⚡️ Ray vs Multiprocessing 벤치마크

👉 [📊 실험 리포트 바로가기](./report/20250415.md)

---

## 📝 프로젝트 개요

이 프로젝트는 동일한 이미지 처리 작업을 두고 두 가지 병렬 처리 방식의 성능을 비교합니다:

- [Ray](https://www.ray.io/) 기반의 분산 처리
- Python 내장 [Multiprocessing](https://docs.python.org/3/library/multiprocessing.html)

실험은 Docker 환경에서 고정된 리소스 설정 하에 수행되며, Ray는 클러스터 구조로 작동하고 Multiprocessing은 프로세스 기반으로 병렬 처리를 수행합니다.

---

## 📁 프로젝트 구조

```
.
├── docs/assets/                    # 시각화 결과 이미지 (output.png)
├── report/                         # 실험 결과 보고서
├── helm/ray-cluster/              # Ray 클러스터 Helm chart (Kubernetes용)
├── run_task_with_ray.py           # Ray 벤치마크 스크립트
├── run_task_with_mp.py            # Multiprocessing 벤치마크 스크립트
├── test_ray.py                    # Ray 클러스터 테스트
├── Dockerfile                     # 벤치마크 컨테이너 정의
├── Makefile                       # 실험 환경 제어용 명령어
├── requirements.txt               # 의존성 정의
```

---

## 🔬 벤치마크 기준 및 작업 설명

### ✅ 비교 목적

동일한 조건에서 **Ray 분산 처리**와 **Python Multiprocessing** 기반 병렬 처리의 실행 시간과 메모리 효율을 비교합니다.

### 🧪 처리 작업 내용

- 무작위 RGB 이미지를 생성 후
- **Gaussian Blur** 필터를 직접 구현해 연산
- **히스토그램 평활화**를 각 채널별로 수행

이 모든 작업은 CPU 연산 중심으로 구성되어 있으며, 실제 서비스에서 흔히 발생할 수 있는 이미지 후처리 파이프라인을 시뮬레이션합니다.

---

## ☁️ Ray Job 등록 방법

Ray 클러스터에 직접 Job을 CLI로 제출하려면 아래 명령을 사용할 수 있습니다:

```bash
ray job submit \
  --address http://localhost:8265 \
  --working-dir ./ \
  -- python run_task_with_ray.py
```

> Ray 클러스터가 사전에 실행 중이어야 하며, 포트포워딩이 설정된 상태여야 합니다:
>
> ```bash
> kubectl port-forward svc/raycluster-kuberay-head 8265:8265
> ```
>
> Ray 클러스터 구성 및 배포는 [공식 문서](https://docs.ray.io/en/latest/cluster/kubernetes/k8s-overview.html)를 참고하세요.

---

## 🛠 Makefile 설명

다음 명령어를 통해 실험 환경을 제어할 수 있습니다:

```bash
make help          # 사용 가능한 명령어 설명 출력
make build         # Docker 이미지 빌드
make run           # 벤치마크 컨테이너 실행
make clean         # 빌드한 이미지 제거
make upgrade-helm  # Helm으로 Ray 클러스터 설치 또는 업그레이드bash
```

### 정의된 변수들

Makefile 내에서 사용되는 주요 변수들은 다음과 같습니다:

- `IMAGE_NAME`: 생성할 Docker 이미지 이름 (`mp-benchmark-test`)
- `CONTAINER_NAME`: 컨테이너 실행 시 사용할 이름 (`mp-benchmark-container`)
- `MEMORY_LIMIT`: Docker 컨테이너 메모리 제한 (`6g`)
- `CPU_LIMIT`: Docker 컨테이너 CPU 제한 (`4`)

`make help` 명령어를 통해 위 변수와 명령어들을 쉽게 확인할 수 있습니다.

---

## 🧠 요약

- CPU 기반 이미지 후처리 작업을 기준으로 병렬 프레임워크 성능을 비교
- Ray Job CLI 사용법 학습 및 Kubernetes Ray 클러스터 연동
- 실험 재현 가능한 환경 구성 (Makefile + Docker + Helm)
