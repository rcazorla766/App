# MLOps GitOps Application

Repositorio de aplicación del TFM:

**"Uso de GitOps para la Gobernanza de Modelos de IA en Producción (MLOps + DevOps)"**

Servicio de inferencia para un modelo de regresión (California Housing) expuesto mediante **FastAPI**, empaquetado con **Docker** y preparado para una futura integración GitOps con **Kubernetes** y **Argo CD**.

---

## Estado del proyecto

| Fase | Estado |
|---|---|
| API de inferencia | ✅ Implementada |
| Entrenamiento offline | ✅ Implementado |
| Tests automatizados | ✅ 99 tests |
| Docker producción | ✅ Dockerfile optimizado |
| Manifiestos Kubernetes (Kustomize) |
| GitOps / Argo CD | 
| CI/CD (GitHub Actions + GHCR) | 

---

## Arquitectura

```
App/
├── app/
│   ├── main.py                 # Punto de entrada FastAPI
│   ├── api/routes/             # Endpoints REST
│   ├── core/                   # Configuración y constantes ML
│   ├── schemas/                # Contratos Pydantic
│   ├── services/               # Lógica de inferencia
│   ├── models/                 # Artefactos del modelo (.pkl + metadata)
│   ├── static/                 # Frontend estático
│   └── templates/              # UI HTML
├── training/
│   └── train_model.py          # Pipeline de entrenamiento offline
├── test/                       # Tests unitarios e integración
├── Dockerfile                  # Imagen de inferencia
├── requirements.txt            # Dependencias de producción
└── requirements-test.txt       # Dependencias de testing
```

**Separación entrenamiento / inferencia:**

- **Entrenamiento:** script manual en `training/` (no incluido en la imagen Docker).
- **Inferencia:** servicio FastAPI que carga el artefacto desde `app/models/`.

---

## Requisitos

- Python **3.12+**
- pip
- Docker Desktop (para ejecución en contenedor)

---

## Ejecución local

### 1. Entorno virtual

```bash
python -m venv venv
```

**Windows (PowerShell):**

```powershell
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
python -m pip install -r requirements.txt
```

### 3. Entrenar el modelo (opcional)

Si no existe `app/models/trained_model_v1.pkl`:

```bash
python training/train_model.py
```

Genera:

- `app/models/trained_model_v1.pkl`
- `app/models/model_metadata.json`

### 4. Arrancar la API

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Verificar endpoints

| Recurso | URL |
|---|---|
| UI | http://localhost:8000/ |
| Swagger | http://localhost:8000/docs |
| Health (liveness) | http://localhost:8000/health |
| Ready (readiness) | http://localhost:8000/ready |
| Metadata del modelo | http://localhost:8000/model |

**Ejemplo de predicción:**

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "MedInc": 8.3252,
    "HouseAge": 41.0,
    "AveRooms": 6.9841,
    "AveBedrms": 1.0238,
    "Population": 322.0,
    "AveOccup": 2.5556,
    "Latitude": 37.88,
    "Longitude": -122.23
  }'
```

Respuesta esperada:

```json
{
  "prediction": 4.37,
  "model_version": "v1"
}
```

---

## Ejecución con Docker

### Construir imagen

```bash
docker build -t ai-house-predictor:latest .
```

### Ejecutar contenedor

```bash
docker run --rm -p 8000:8000 ai-house-predictor:latest
```

### Variables de entorno soportadas

| Variable | Descripción | Default |
|---|---|---|
| `MODEL_PATH` | Ruta al modelo `.pkl` | `/app/app/models/trained_model_v1.pkl` |
| `MODEL_METADATA_PATH` | Ruta al JSON de metadata | `/app/app/models/model_metadata.json` |
| `HOST` | Host de Uvicorn | `0.0.0.0` |
| `PORT` | Puerto HTTP | `8000` |

**Ejemplo con variables personalizadas:**

```bash
docker run --rm -p 8080:8080 \
  -e PORT=8080 \
  -e MODEL_PATH=/app/app/models/trained_model_v1.pkl \
  ai-house-predictor:latest
```

### Healthcheck del contenedor

El `Dockerfile` incluye un `HEALTHCHECK` que consulta `GET /health` cada 30 segundos.

Verificar estado:

```bash
docker ps
docker inspect --format='{{json .State.Health}}' <container_id>
```

---

## Tests

```bash
python -m pip install -r requirements.txt -r requirements-test.txt
python -m pytest
```

---

## Dependencias principales

| Paquete | Versión | Uso |
|---|---|---|
| fastapi | 0.137.1 | API REST |
| uvicorn | 0.49.0 | Servidor ASGI |
| pydantic | 2.13.4 | Validación |
| scikit-learn | 1.9.0 | Modelo ML |
| joblib | 1.5.3 | Serialización |
| numpy | 2.4.6 | Operaciones numéricas |
| pandas | 3.0.3 | Datetime durante entrenamiento |

---

## Despliegue en Kubernetes

Los manifiestos declarativos viven en el repositorio **`Config/`** y se gestionan con **Kustomize**.

### Estructura

```
Config/
├── base/                    # Despliegue base (2 réplicas)
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── secret.example.yaml
│   └── kustomization.yaml
└── overlays/
    ├── dev/                 # 1 réplica, LOG_LEVEL=debug
    └── prod/                # 2 réplicas, más recursos
```

### Prerrequisitos

- Clúster Kubernetes operativo (Docker Desktop Kubernetes, k3s, AKS, etc.)
- `kubectl` configurado
- Imagen Docker construida y disponible en el clúster

### 1. Construir la imagen

```bash
cd App
docker build -t ai-house-predictor:1.0.0 .
```

> En clústeres locales (k3s/kind/minikube), importa la imagen al runtime del nodo si no usas un registry.

### 2. Desplegar con Kustomize

**Base (recomendado para validación del TFM):**

```bash
kubectl apply -k Config/base
```

**Entorno dev:**

```bash
kubectl apply -k Config/overlays/dev
```

**Entorno prod:**

```bash
kubectl apply -k Config/overlays/prod
```

### 3. Verificar el despliegue

```bash
kubectl -n mlops-house-predictor get pods
kubectl -n mlops-house-predictor get deployments
kubectl -n mlops-house-predictor get svc
kubectl -n mlops-house-predictor describe deployment ai-house-predictor
kubectl -n mlops-house-predictor rollout status deployment/ai-house-predictor
kubectl -n mlops-house-predictor rollout history deployment/ai-house-predictor
```

### 4. Probar la API dentro del clúster

**Opción A — Pod temporal con curl:**

```bash
kubectl -n mlops-house-predictor run api-test --rm -it --restart=Never \
  --image=curlimages/curl:8.12.1 -- \
  curl -s http://ai-house-predictor/health
```

**Opción B — Port-forward desde tu máquina:**

```bash
kubectl -n mlops-house-predictor port-forward svc/ai-house-predictor 18080:80
```

Luego:

| Endpoint | URL |
|---|---|
| Health | http://localhost:18080/health |
| Ready | http://localhost:18080/ready |
| Model | http://localhost:18080/model |
| Predict | `POST http://localhost:18080/predict` |

### Recursos desplegados

| Recurso | Nombre | Detalle |
|---|---|---|
| Namespace | `mlops-house-predictor` | Aislamiento del servicio |
| Deployment | `ai-house-predictor` | 2 réplicas, RollingUpdate |
| Service | `ai-house-predictor` | ClusterIP :80 → :8000 |
| ConfigMap | `ai-house-predictor-config` | HOST, PORT, MODEL_PATH, etc. |

### Configuración externalizada (ConfigMap)

Toda la configuración de la aplicación se inyecta mediante `envFrom`:

- `MODEL_PATH`, `MODEL_METADATA_PATH`
- `HOST`, `PORT`
- `APP_NAME`, `LOG_LEVEL`, `ENVIRONMENT`

### Secret de ejemplo

`Config/base/secret.example.yaml` documenta credenciales futuras (MLflow, API keys). **No se aplica** en el despliegue base. En Sprint 3 (GitOps) se gestionará con Sealed Secrets o External Secrets.

### Documentación Sprint 2

Informe completo: [`../Config/SPRINT2_REPORT.md`](../Config/SPRINT2_REPORT.md)

---

## GitOps con Argo CD

A partir del **Sprint 3**, el despliegue productivo está gobernado por **Argo CD**. Git es la única fuente de verdad.

### Arquitectura

```
Desarrollador → git push (Config/overlays/prod) → GitHub → Argo CD → Kubernetes
```

| Componente | Ubicación |
|---|---|
| Manifiestos Kustomize | Repositorio `Config/` |
| Application Argo CD | `Config/argocd/application.yaml` |
| Entorno productivo | `overlays/prod` → namespace `mlops-house-predictor-prod` |

### Instalar Argo CD (bootstrap único)

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl apply -f Config/argocd/application.yaml
```

> A partir de aquí **no usar** `kubectl apply -k` para desplegar la aplicación.

### Acceder a la UI de Argo CD

```bash
kubectl -n argocd port-forward svc/argocd-server 8443:443
```

Abrir **https://localhost:8443** (usuario: `admin`).

Obtener contraseña inicial:

```bash
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d
```

### Política de sincronización

| Opción | Valor | Efecto |
|---|---|---|
| `automated.prune` | `true` | Elimina recursos no declarados en Git |
| `automated.selfHeal` | `true` | Corrige drift manual en el clúster |
| `syncOptions` | `CreateNamespace=true` | Crea namespace automáticamente |

### Flujo de cambio (GitOps)

1. Editar manifiestos en `Config/overlays/prod/`.
2. `git commit` + `git push origin main`.
3. Argo CD detecta el cambio y sincroniza.
4. Kubernetes ejecuta RollingUpdate si cambia el Deployment.

### Verificar estado

```bash
kubectl -n argocd get applications
kubectl -n argocd describe application ai-house-predictor-prod
kubectl -n mlops-house-predictor-prod get pods,deploy,svc
```

### Documentación Sprint 3

Informe completo con pruebas GitOps: [`../Config/SPRINT3_REPORT.md`](../Config/SPRINT3_REPORT.md)

---

## CI/CD con GitHub Actions y GHCR

A partir del **Sprint 4**, cada `push` a `main` dispara el pipeline completo **sin `kubectl apply`**.

### Flujo automatizado

```
push main (App) → pytest → Docker Buildx → GHCR → update Config/overlays/prod → Argo CD → Kubernetes
```

### Workflow

Archivo: [`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml)

| Evento | Acción |
|---|---|
| `pull_request` → `main` | Solo tests (`pytest`) |
| `push` → `main` | Tests + build + push GHCR + update GitOps |

### Tags de imagen

| Tag | Ejemplo | Uso |
|---|---|---|
| `{short_sha}` | `f643a78` | Despliegue en prod (GitOps) |
| `run-{number}` | `run-42` | Trazabilidad de ejecución CI |

Imagen: `ghcr.io/<owner>/ai-house-predictor:<tag>`

### Secretos requeridos (repo App)

| Secreto | Descripción |
|---|---|
| `GITHUB_TOKEN` | Automático — publicación en GHCR |
| `CONFIG_REPO_TOKEN` | PAT con permiso `write` sobre repo `Config` |

Configurar en: **App → Settings → Secrets and variables → Actions**

### Actualización GitOps

El pipeline ejecuta en el repo `Config`:

```bash
kustomize edit set image ai-house-predictor=ghcr.io/<owner>/ai-house-predictor:<short_sha>
git commit -m "ci(app): update prod image to ..."
git push origin main
```

Argo CD detecta el cambio y sincroniza automáticamente.

### Documentación Sprint 4

Informe completo: [`SPRINT4_REPORT.md`](SPRINT4_REPORT.md)

---

## Documentación adicional

- Auditoría técnica completa: [`PROJECT_AUDIT.md`](PROJECT_AUDIT.md)
- Manifiestos GitOps (repositorio separado): `mlops-gitops-config`

---

## Autores

Máster en Desarrollo y Operaciones (DevOps)  
Universidad Internacional de La Rioja (UNIR)

Rubén Cazorla Rodríguez  
Cristhian Alexander Cano Correa
