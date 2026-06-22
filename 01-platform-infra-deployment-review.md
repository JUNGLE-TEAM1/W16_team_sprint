# 01. 플랫폼/인프라/배포 리뷰 초안

작성자: 1번 담당  
작성일: 2026-06-21  
리뷰 범위: Docker Compose, Kubernetes manifests, Helm chart, EKS/ECR/S3/ALB/IRSA, CI/CD, 이미지 태그, 배포/롤백, 운영 관측성, 보안/비용 리스크

## 1. 담당 범위

XFlow가 로컬 개발 환경과 Kubernetes/AWS 환경에서 어떻게 실행되고 배포되는지 검토한다. 이번 리뷰의 핵심 질문은 다음이다.

> XFlow는 로컬에서 쉽게 띄울 수 있고, 운영 환경에서는 안전하게 배포·롤백·관측·복구할 수 있는 구조인가?

## 2. 먼저 확인한 파일

| 경로 | 확인한 내용 |
|---|---|
| `docker-compose.yml` | 로컬 전체 서비스 구성, 평문 credential, Docker socket mount, LocalStack, OpenSearch security 설정 |
| `k8s/` | raw Kubernetes manifest, Kustomize 구성, ALB Ingress, ECR 이미지, Secret, ServiceAccount, RBAC |
| `k8s/airflow/`, `k8s/kafka/`, `k8s/trino/`, `k8s/monitoring/`, `k8s/spark/` | Airflow/Strimzi Kafka/Trino/Grafana-Loki/Spark Operator 관련 별도 배포 설정 |
| `charts/xflow/` | 통합 Helm chart, cloud별 values, subchart 의존성, 자체 template |
| `infra/README.md` | EKS/ECR/S3/ALB/ACM/Route53/Helm 배포 절차 |
| `infra/cluster.yaml` | EKS cluster, IRSA, node group, S3 endpoint, CloudWatch logging |
| `infra/setup.sh` | ECR/S3/EKS/LB controller 생성 자동화, 이미지 빌드/푸시 함수 |
| `.github/workflows/` | backend/airflow/spark/frontend CI/CD 흐름 |
| `backend/Dockerfile`, `airflow/Dockerfile`, `spark/Dockerfile.*` | 이미지 빌드 방식과 runtime 의존성 |
| `terraform/localstack/` | LocalStack용 Terraform, 실제 AWS 운영 IaC는 아님 |

## 3. 현재 구조 요약

### 로컬

`docker-compose.yml` 하나로 개발용 풀스택을 실행한다. 구성 요소는 PostgreSQL, Neo4j, MongoDB, Backend, Airflow webserver/scheduler/init, Spark master/worker, Zookeeper, Kafka, Schema Registry, Kafka Connect, Kafka UI, Hive Metastore, Trino, LocalStack Pro, OpenSearch, OpenSearch Dashboards다.

로컬 환경은 기능 검증에는 강하다. CDC, S3 유사 환경, 검색, SQL 엔진, Airflow, Spark를 한 번에 띄울 수 있다. 다만 `postgres/postgres`, `admin/admin`, `mongo/mongo`, `neo4j/password` 같은 기본 credential이 그대로 있고, backend/Airflow/LocalStack이 `/var/run/docker.sock`을 mount한다.

### Kubernetes

Kubernetes 배포 경로는 두 갈래다.

첫째, `k8s/` raw manifest와 Kustomize가 있다. `k8s/kustomization.yaml` 기준으로는 `xflow` namespace에 backend, MongoDB, OpenSearch, OpenSearch Dashboards 정도가 포함된다. 그 외 Airflow, Kafka, Trino, monitoring, Spark manifest는 별도 폴더에 따로 존재한다.

둘째, `charts/xflow/` 통합 Helm chart가 있다. Helm chart는 backend, MongoDB, OpenSearch, Spark template을 직접 가지고 있고, Airflow, Trino, Grafana, Loki는 official chart를 dependency로 사용한다. EKS/GKE/AKS/Minikube용 values가 분리되어 있다.

### Helm

Helm chart는 XFlow를 멀티 클라우드에 배포하려는 방향성을 보여준다. `values-eks.yaml`, `values-gke.yaml`, `values-aks.yaml`, `values-minikube.yaml`이 있고, `Chart.yaml`에는 Airflow, Trino, Grafana, Loki 의존성이 정의되어 있다. `charts/xflow/charts/` 안에 dependency tgz도 들어 있어 이론상 네트워크 없이 렌더링 가능하다.

하지만 실제 운영 값은 여러 곳에 흩어져 있다. `values-eks.yaml`은 placeholder가 많고, `values-eks-test.yaml`과 raw `k8s/` manifest에는 특정 AWS account ID, ECR 주소, ACM ARN, 도메인이 하드코딩되어 있다.

### EKS/AWS

`infra/cluster.yaml`은 `eksctl` 기반 EKS 구성을 정의한다.

- region: `ap-northeast-2`
- cluster version: `1.29`
- OIDC enabled
- general node group: `t3.large`, desired 2, min 1, max 4
- Spark node group: `m5.xlarge`/`m5.2xlarge`, Spot, min 0, max 5, taint 적용
- S3 Gateway Endpoint
- CloudWatch control-plane logging
- EBS CSI driver addon

AWS 리소스는 `infra/setup.sh`와 `infra/README.md`에서 ECR repo, S3 bucket, EKS cluster, AWS Load Balancer Controller, ACM, Route53, Helm 배포를 순서대로 안내한다.

### 이미지 빌드/배포

GitHub Actions가 있다.

- `deploy-backend.yml`: backend 변경 시 ECR에 `latest`와 `github.sha` 태그 push 후 EKS deployment restart
- `deploy-airflow.yml`: Airflow image push 후 Airflow webserver/scheduler/triggerer restart
- `deploy-spark.yml`: Spark image push만 수행
- `deploy-frontend.yml`: frontend build 후 S3 sync, CloudFront invalidation

배포는 전체적으로 `latest`에 의존한다. SHA 태그도 push하지만 manifest나 Helm values를 SHA로 갱신하지 않기 때문에 실제 배포 버전을 정확히 고정하지 못한다.

## 4. 이 구조가 필요한 이유

| 구성 요소 | 필요한 이유 | 대체 가능성 |
|---|---|---|
| Docker Compose | 개발자가 로컬에서 XFlow 전체 기능을 빠르게 검증하기 위해 필요 | 개발용 Tilt/Skaffold/DevContainer |
| Kubernetes | backend, Airflow, Spark, Kafka, OpenSearch, Trino 같은 여러 컴포넌트를 운영 환경에서 관리하기 위해 필요 | 작은 MVP라면 ECS/Fargate 일부 대체 가능 |
| Helm | 환경별 values로 배포 설정을 관리하고 반복 배포하기 위해 필요 | Kustomize 단일화 가능하지만 subchart 관리에는 Helm이 유리 |
| EKS | AWS에서 Kubernetes 기반 데이터 플랫폼을 운영하기 위한 관리형 control plane | ECS/Fargate, managed workflow 조합 |
| ECR | backend/Airflow/Spark 이미지를 AWS 내부 registry에서 관리하기 위해 필요 | DockerHub, GitHub Container Registry |
| S3 | 데이터 레이크, Airflow logs, Loki logs 저장소로 필요 | MinIO, GCS, Azure Blob |
| ALB/Ingress/TLS | backend/Grafana/Airflow/Trino/OpenSearch UI를 외부에서 HTTPS로 접근하기 위해 필요 | Nginx Ingress + cert-manager, CloudFront/API Gateway 일부 대체 |
| IRSA | Pod별 AWS 권한을 node role이 아니라 ServiceAccount 단위로 분리하기 위해 필요 | static key는 지양, EKS Pod Identity도 검토 가능 |

## 5. 현재 구조의 장점

- 로컬 개발 환경이 풍부하다. Compose만 보면 데이터 플랫폼의 주요 구성요소를 한 번에 띄울 수 있다.
- 운영 배포를 고려한 자산이 이미 있다. EKS cluster 설정, Helm chart, raw manifest, GitHub Actions, ALB Ingress, IRSA 문서가 존재한다.
- Helm chart가 멀티 클라우드 values 구조를 갖고 있어 EKS/GKE/AKS/Minikube 방향성을 비교하기 쉽다.
- backend, MongoDB, OpenSearch에는 resource request/limit과 readiness/liveness probe가 들어가 있다.
- EKS 설정에 S3 Gateway Endpoint와 control-plane CloudWatch logging이 포함되어 있어 비용과 감사 관점을 어느 정도 고려했다.
- Spark 전용 namespace와 Spot node group을 두려는 설계가 있어 대용량 job 비용 절감 방향이 보인다.
- Grafana + Loki + CloudWatch datasource 구성이 있어 운영 로그 관측성의 골격이 있다.

## 6. 위험하거나 애매한 부분

| 항목 | 현재 상태 | 왜 위험한가 | 근거 파일 |
|---|---|---|---|
| 배포 source of truth | `docker-compose.yml`, `k8s/`, `charts/xflow/`, `k8s/*/values.yaml`, `infra/setup.sh`가 병행 | 어떤 설정이 운영 기준인지 모호하면 장애 시 재현/복구가 어렵다 | `docker-compose.yml`, `k8s/`, `charts/xflow/`, `infra/setup.sh` |
| namespace 불일치 | Helm은 Airflow를 `xflow` namespace subchart로 보는 반면, standalone workflow/manifests는 `airflow` namespace를 사용 | CI/CD가 실제 설치 위치와 다르면 restart/rollout이 실패할 수 있다 | `charts/xflow/values-eks.yaml`, `.github/workflows/deploy-airflow.yml`, `k8s/airflow/values.yaml` |
| 이미지 태그 전략 | 대부분 `latest` 사용. SHA는 push하지만 배포 manifest는 갱신하지 않음 | 어떤 코드가 운영 중인지 추적하기 어렵고, rollback도 불명확하다 | `.github/workflows/deploy-backend.yml`, `charts/xflow/values.yaml`, `k8s/backend/deployment.yaml` |
| secret 주입 방식 | K8s Secret과 values에 평문 비밀번호/URL이 들어감 | repo 유출 시 credential이 바로 노출된다 | `k8s/backend/secret.yaml`, `k8s/mongodb/secret.yaml`, `k8s/monitoring/grafana-secret.yaml`, `k8s/airflow/values.yaml` |
| IAM 권한 | 여러 ServiceAccount에 `AmazonS3FullAccess`, Trino에 `AWSGlueConsoleFullAccess` | 최소 권한 원칙 위반. 침해 시 피해 범위가 전체 S3/Glue로 커진다 | `infra/cluster.yaml` |
| CI/CD 인증 | GitHub Actions가 AWS access key/secret을 사용 | 장기 키 관리 부담이 있고 OIDC 기반 단기 권한보다 위험하다 | `.github/workflows/*.yml` |
| Stateful 서비스 운영 | MongoDB, OpenSearch, Kafka, Airflow PostgreSQL을 직접 운영하고 대부분 단일 replica | PV 장애, 노드 장애, 디스크 부족 시 복구 부담이 크다 | `k8s/mongodb/`, `k8s/opensearch/`, `k8s/kafka/`, `charts/xflow/values.yaml` |
| OpenSearch 보안 | security plugin disabled | 외부 노출 또는 내부 침해 시 검색 인덱스 접근 통제가 약하다 | `docker-compose.yml`, `k8s/opensearch/statefulset.yaml`, `charts/xflow/values.yaml` |
| backend 운영 이미지 | Dockerfile CMD가 `uvicorn --reload` | 운영에서 reload watcher는 불필요하고 안정성/성능에 불리하다 | `backend/Dockerfile` |
| 수동 운영 절차 | Airflow variables/connections를 `kubectl exec`로 다시 설정해야 한다고 문서화 | 클러스터 재생성/업그레이드 후 누락 가능성이 높다 | `k8s/airflow/AWS_IAM_CONFIG.md` |
| deploy script 완성도 | `infra/setup.sh`에 Helm 배포 함수가 있지만 main에서 호출하지 않음 | "자동 설정"이라고 보기 어렵고 실제 배포 단계가 수동으로 남는다 | `infra/setup.sh` |
| Minikube 배포 스크립트 불일치 | `k8s/deploy.sh`는 `xflow-backend:latest`를 로컬 빌드하지만, manifest는 ECR 이미지를 사용하고 Kustomize에는 `backend-sa`가 빠져 있음 | 로컬 k8s 배포가 이미지 pull 또는 ServiceAccount 누락으로 실패할 수 있다 | `k8s/deploy.sh`, `k8s/backend/deployment.yaml`, `k8s/kustomization.yaml` |
| raw manifest 하드코딩 | AWS account ID, ECR URL, ACM ARN, 도메인이 직접 들어감 | 다른 계정/환경 재사용이 어렵고 민감 운영 정보가 repo에 남는다 | `k8s/ingress.yaml`, `k8s/backend/configmap.yaml`, `k8s/airflow/values.yaml` |

## 7. 운영 시 장애 가능성

| 장애 시나리오 | 영향 범위 | 탐지 방법 | 복구 방법 | 개선 필요 |
|---|---|---|---|---|
| 이미지 배포 실패 | backend/Airflow/Spark 신규 기능 배포 중단 | GitHub Actions 실패, ECR push 실패 | 이전 이미지 태그로 재배포 | immutable tag + rollback 절차 필요 |
| `latest` 이미지 불일치 | pod마다 서로 다른 build 실행 가능 | pod image digest 확인 | digest/SHA tag로 고정 | Must Fix |
| Helm upgrade 실패 | 여러 컴포넌트 동시 변경 중 일부 실패 | `helm status`, `kubectl get events` | `helm rollback` | Helm 단일 source of truth 필요 |
| ALB/Ingress/TLS 오류 | API, Grafana, Airflow, Trino, OpenSearch UI 외부 접근 실패 | `kubectl describe ingress`, ALB target health | ACM/DNS/Ingress annotation 수정 | 도메인/ACM 값 외부화 필요 |
| S3 권한 오류 | Spark ETL, Trino, Airflow log, Loki log 실패 | pod logs, CloudTrail, S3 AccessDenied | IRSA policy 수정 | 최소 권한 policy를 리소스별로 분리 |
| MongoDB/OpenSearch PV 장애 | 메타데이터, catalog/search 기능 장애 | pod 상태, PVC events, application errors | snapshot/backup에서 복구 | 백업/managed service 검토 |
| Kafka broker 장애 | CDC/streaming ingest 중단 또는 지연 | Strimzi status, Kafka UI, consumer lag | broker 복구, topic 상태 확인 | replica/minISR 재검토 |
| Spark job pending | batch/streaming job 실행 불가 | SparkApplication status, pod pending reason | node group scale-up, resource 조정 | nodeSelector/toleration/resource profile 정리 |
| Airflow DB/variables 누락 | DAG 실행 실패, backend 연동 실패 | Airflow UI/logs | variables/connections 재등록 | Helm Secret/env/connection bootstrap 자동화 |
| Loki/Grafana 장애 | 장애 추적과 로그 검색 약화 | Grafana/Loki pod logs | helm rollback/reinstall | monitoring도 운영 대상화 필요 |

## 8. 보안/권한/비용 리스크

| 리스크 | 분류 | 현재 근거 | 개선 방향 |
|---|---|---|---|
| 평문 credential | 보안 | compose, K8s Secret, Helm values에 기본 비밀번호 포함 | External Secrets + AWS Secrets Manager/SSM 사용 |
| 과도한 IAM 권한 | 보안 | `AmazonS3FullAccess`, `AWSGlueConsoleFullAccess` | bucket/prefix/action 단위 custom policy |
| GitHub Actions 장기 AWS key | 보안 | `aws-access-key-id`, `aws-secret-access-key` secret 사용 | GitHub OIDC + role assumption |
| `latest` 이미지 사용 | 운영 | backend/Airflow/Spark/Kafka UI 등 | commit SHA 또는 semver tag 고정 |
| OpenSearch security off | 보안 | `plugins.security.disabled=true` | production에서는 security on 또는 managed OpenSearch |
| Stateful 서비스 직접 운영 | 운영/비용 | MongoDB/OpenSearch/Kafka/Airflow PG 단일 운영 | managed service 또는 백업/HA 설계 |
| Single NAT Gateway | 가용성/비용 | 비용 절감 목적의 단일 NAT | MVP는 가능, 운영은 HA NAT 여부 판단 |
| Spark Spot node 사용 | 비용/안정성 | Spark node group이 Spot | 재시도/idempotency 전제 필요 |
| 로그/검색 저장 비용 | 비용 | Loki S3, OpenSearch PVC, Airflow logs | retention, lifecycle, index policy 필요 |
| 멀티 클라우드 values | 유지보수 | EKS/GKE/AKS values 병행 | 실제 목표 클라우드 기준으로 범위 축소 |

## 9. 개선 후보

| 분류 | 개선안 | 기대 효과 | 난이도 | 우선순위 |
|---|---|---|---|---|
| Must Fix | 배포 source of truth를 Helm 중심으로 정리 | 환경별 재현성과 운영 복구성 향상 | 중 | P0 |
| Must Fix | 이미지 태그를 SHA/digest 기반으로 배포하고 `latest` 의존 제거 | 배포 추적과 rollback 가능 | 중 | P0 |
| Must Fix | repo 내 평문 secret 제거 및 External Secrets/Secrets Manager 도입 | credential 노출 위험 감소 | 중 | P0 |
| Must Fix | IRSA 권한을 S3 bucket/prefix/action 단위로 축소 | 침해 범위 제한 | 중 | P0 |
| Should Improve | GitHub Actions를 AWS static key에서 OIDC로 전환 | 장기 키 제거 | 중 | P1 |
| Should Improve | Airflow variables/connections bootstrap을 Helm/K8s Job으로 자동화 | 재설치/업그레이드 안정성 향상 | 중 | P1 |
| Should Improve | backend Dockerfile 운영 CMD에서 `--reload` 제거 | 운영 안정성 향상 | 하 | P1 |
| Should Improve | OpenSearch/Kafka/MongoDB backup/retention/복구 절차 문서화 | stateful 장애 대응 가능 | 중 | P1 |
| Should Improve | monitoring install 절차와 Helm chart 구성 통일 | 장애 추적 경로 명확화 | 중 | P1 |
| Could Improve | managed OpenSearch/MSK/MongoDB Atlas 검토 | 운영 부담 감소 | 중~상 | P2 |
| Could Improve | HPA, PodDisruptionBudget, NetworkPolicy 추가 | 가용성과 격리 강화 | 중 | P2 |
| Research Needed | EKS 전체 운영 vs ECS/Fargate 일부 대체 비교 | 비용/복잡도 절감 판단 | 중 | P2 |
| Research Needed | Spark Operator와 Airflow executor 구조 최적화 | job 실행 안정성 판단 | 중 | P2 |

## 10. 대안 기술 또는 설계

| 현재 방식 | 대안 | 장점 | 단점 | 추천 여부 |
|---|---|---|---|---|
| raw k8s manifests + Helm 병행 | Helm 단일화 | source of truth 명확, rollback 쉬움 | 초반 values 정리 필요 | 추천 |
| eksctl + 수동 스크립트 | Terraform/OpenTofu 또는 AWS CDK | 인프라 변경 추적 가능 | 초기 작성 비용 | 중장기 추천 |
| GitHub Actions static AWS key | GitHub OIDC + IAM role | 장기 키 제거 | IAM 설정 필요 | 강력 추천 |
| `latest` + rollout restart | SHA tag를 values에 주입 후 Helm upgrade | 배포 버전 명확 | workflow 수정 필요 | 강력 추천 |
| 직접 OpenSearch 운영 | Amazon OpenSearch Service | 보안/백업/운영 부담 감소 | 비용 증가 | 운영 전 검토 |
| 직접 Kafka 운영 | MSK/Confluent Cloud | CDC 안정성/운영 부담 감소 | 비용 증가, 설정 복잡 | PoC 후 판단 |
| 직접 MongoDB 운영 | MongoDB Atlas/DocumentDB | 백업/HA 단순화 | 비용/호환성 검토 필요 | PoC 후 판단 |
| EKS 모든 컴포넌트 운영 | 일부 ECS/Fargate/managed service 조합 | 운영 복잡도 감소 | Spark/K8s job 제어와 분리 필요 | Research Needed |

## 11. 다른 영역과 연결되는 지점

| 연결 영역 | 인터페이스 | 맞춰야 할 내용 |
|---|---|---|
| 데이터 실행/오케스트레이션 | Spark namespace, Airflow endpoint, Kafka endpoint, SparkApplication RBAC | `spark-jobs` namespace, Airflow namespace, Kafka bootstrap 주소, job resource profile |
| 저장소/쿼리/검색 | S3 bucket, Glue/Hive metastore, Trino catalog, OpenSearch endpoint/PV | bucket naming, warehouse path, catalog source of truth, OpenSearch security/backup |
| 백엔드/보안/관측성 | backend env, secret, service account, ingress, logs, metrics | env var 계약, Secret reference, IRSA role, API host, 로그 수집 기준 |
| 프론트엔드/발표 데모 | S3/CloudFront, API domain, CORS, TLS | `app/api` 도메인, HTTPS, CORS origin, CloudFront invalidation |

## 12. 최종 추천안

```text
유지할 것:
- Docker Compose 기반 로컬 풀스택 개발 환경
- EKS + Helm 기반 운영 배포 방향
- Spark 전용 namespace와 Spot node group 설계
- ALB Ingress + ACM + Route53 기반 HTTPS 접근 구조
- Grafana/Loki/CloudWatch를 이용한 로그 관측성 방향

반드시 고칠 것:
- Helm과 raw manifest 중 운영 source of truth를 하나로 정리
- latest 이미지 의존 제거, SHA/digest 기반 배포와 rollback 기준 수립
- 평문 secret 제거, External Secrets/Secrets Manager 연동
- AmazonS3FullAccess/AWSGlueConsoleFullAccess를 최소 권한으로 축소
- GitHub Actions의 AWS static key를 OIDC 기반 role assumption으로 변경

단기 개선:
- backend Dockerfile에서 --reload 제거
- Airflow variables/connections 자동 bootstrap
- namespace와 service 이름 계약 정리
- k8s/monitoring README와 실제 파일 불일치 정리
- values-eks.yaml에 실제 운영 필수값과 테스트값 분리

장기 개선:
- MongoDB/OpenSearch/Kafka 직접 운영 vs managed service 비교
- Terraform/OpenTofu/CDK로 AWS 인프라 IaC 단일화
- HPA, PDB, NetworkPolicy, backup/restore, retention policy 추가
- 배포 환경별 비용 산정과 알림 기준 정리

추가 PoC:
- Helm chart를 EKS test cluster에 SHA tag로 배포/rollback
- IRSA 최소 권한으로 S3 read/write, Airflow log, Trino Glue 접근 검증
- ALB Ingress + ACM + DNS end-to-end 검증
- Spark Spot node interruption 시 retry/idempotency 검증
```

## 13. 발표용 한 줄 결론

XFlow는 로컬 실행과 EKS 배포를 모두 고려한 꽤 큰 데이터 플랫폼 구조를 갖고 있지만, 현재 운영 관점에서는 `latest` 이미지, 평문 secret, 과도한 IAM, raw manifest와 Helm 병행 때문에 재현성과 보안이 약하다. 따라서 1번 담당의 핵심 개선 방향은 **Helm 중심 배포 표준화, immutable image tag, secret/IAM 정리, CI/CD rollback 가능화**다.

## 14. 확인한 검증

- `kubectl kustomize k8s` 실행 성공. raw `k8s/` Kustomize 기준 렌더링은 가능했다.
- `helm lint charts/xflow`, `helm template ...`는 현재 로컬 환경에 `helm` 명령이 없어 실행하지 못했다.
