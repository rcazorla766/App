# PROJECT_AUDIT.md

**Proyecto:** MLOps GitOps Application (TFM UNIR)  
**Fecha:** 29 de junio de 2026  
**Alcance:** Fase 1 — Auditoría técnica y preparación para GitOps (sin Kubernetes/Argo CD)

---

## 1. Arquitectura encontrada

### 1.1 Stack tecnológico

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.12+ |
| API | FastAPI 0.137.1 + Uvicorn |
| Validación | Pydantic v2 |
| ML | scikit-learn, joblib, numpy, pandas |
| Contenedor | Docker (python:3.12-slim-bookworm) |
| Tests | pytest + httpx |

### 1.2 Estructura del repositorio

```
App/
├── app/
│   ├── main.py
│   ├── api/routes/          # health, ready, predict, model
│   ├── core/                # config.py, constants.py
│   ├── schemas/
│   ├── services/            # PredictionService
│   ├── models/              # trained_model_v1.pkl + metadata
│   ├── static/
│   └── templates/
├── training/
│   └── train_model.py       # Entrenamiento offline
├── test/
├── Dockerfile
├── requirements.txt
└── requirements-test.txt
```

### 1.3 Flujo de entrenamiento

1. `training/train_model.py` descarga **California Housing** vía sklearn.
2. Entrena **RandomForestRegressor** (100 árboles, max_depth=10).
3. Evalúa RMSE y R² en consola.
4. Persiste:
   - `app/models/trained_model_v1.pkl` (~10 MB)
   - `app/models/model_metadata.json`

### 1.4 Flujo de inferencia

1. Al arrancar, `PredictionService` carga modelo y metadata desde disco.
2. `POST /predict` valida 8 features con Pydantic.
3. El servicio ordena features según `FEATURE_NAMES` y ejecuta `model.predict()`.
4. Respuesta: `{ prediction, model_version }`.

### 1.5 Almacenamiento de modelos

| Artefacto | Ubicación | En Git | En imagen Docker |
|---|---|---|---|
| Modelo | `app/models/trained_model_v1.pkl` | Sí | Sí |
| Metadata | `app/models/model_metadata.json` | Sí | Sí |
| Dataset | Descargado en runtime (entrenamiento) | No | No (excluido) |

### 1.6 Desacoplamiento entrenamiento / inferencia

| Aspecto | Estado |
|---|---|
| Código separado (`training/` vs `app/`) | ✅ Sí |
| Imagen Docker sin código de entrenamiento | ✅ Sí (`.dockerignore`) |
| Dependencias separadas (train vs inference) | ⚠ Parcial (mismas deps ML) |
| Registro de modelos externo (MLflow/S3) | ❌ No |
| Pipeline CI de entrenamiento | ❌ No |

**Conclusión:** Desacoplamiento **lógico y de empaquetado**, pero el modelo sigue embebido en el repositorio y en la imagen.

---

## 2. Problemas detectados

### 2.1 Críticos (corregidos en esta fase)

| # | Problema | Impacto |
|---|---|---|
| C1 | Rutas hardcodeadas sin variables de entorno | Imposible montar modelos externos en K8s |
| C2 | `dockerfile` en minúsculas (no estándar) | Fallos en CI Linux |
| C3 | Sin HEALTHCHECK en Docker | No apto para orquestadores |
| C4 | Contenedor ejecutaba como root | Riesgo de seguridad |
| C5 | `httpx2` incorrecto en requirements-test | Tests no instalables |
| C6 | Metadata JSON manual, no generada por entrenamiento | Deriva entre modelo y metadata |
| C7 | Features duplicadas en training e inferencia | Riesgo de desalineación |

### 2.2 Altos (pendientes)

| # | Problema | Impacto |
|---|---|---|
| A1 | Modelo versionado en Git (~10 MB) | Repositorio pesado, mala práctica MLOps |
| A2 | Sin MLflow ni registro de experimentos | Sin trazabilidad ML |
| A3 | `/health` no validaba carga del modelo | Falsos positivos en probes |
| A4 | Sin endpoint para `reload_model()` | Hot-reload no operativo |
| A5 | CI existente no alineado con nuevo `Dockerfile` | Riesgo en fase GitOps |
| A6 | Sin `requirements-train.txt` separado | Imagen de inferencia incluye deps innecesarias |

### 2.3 Medios

| # | Problema |
|---|---|
| M1 | Código comentado en `main.py` (eliminado) |
| M2 | README desactualizado respecto a estructura real |
| M3 | `pandas` en producción sin uso en inferencia |
| M4 | UI con metadata hardcodeada en HTML |
| M5 | Sin logging estructurado |
| M6 | Sin límites de recursos documentados |

### 2.4 Código duplicado detectado

| Elemento | Ubicaciones | Estado |
|---|---|---|
| Lista de 8 features | `prediction_service.py`, `train_model.py` | ✅ Centralizado en `app/core/constants.py` |
| Metadata del modelo | JSON manual + constantes | ✅ Generado por script de entrenamiento |
| Imports duplicados en routes | `prediction.py` | ⚠ Menor, sin impacto |

---

## 3. Riesgos para producción

| Riesgo | Severidad | Descripción |
|---|---|---|
| Modelo embebido en imagen | Alta | Cada cambio de modelo requiere rebuild completo |
| Sin readiness real histórico | Media | Corregido con `/ready` |
| Pickle como formato | Alta | Inseguro e incompatible entre versiones sklearn |
| Sin autenticación/autorización | Alta | API expuesta sin control de acceso |
| Sin rate limiting | Media | Vulnerable a abuso |
| Sin observabilidad | Alta | Sin métricas, traces ni logs centralizados |
| Sin secretos gestionados | Alta | Futuro: credenciales MLflow, registry |
| Single replica sin HPA | Media | Sin escalado automático |
| Docker Desktop no disponible en auditoría | Baja | Build no verificado en contenedor real |

---

## 4. Recomendaciones

### Prioridad 1 — Antes de GitOps

1. Externalizar artefactos a object storage (S3/MinIO/Azure Blob).
2. Integrar **MLflow** para versionado y métricas.
3. Sustituir pickle por **MLflow pyfunc** o **ONNX**.
4. Crear manifiestos K8s en repositorio `Config/`.
5. Configurar probes: liveness=`/health`, readiness=`/ready`.

### Prioridad 2 — GitOps

6. Pipeline CI: test → build → push GHCR → actualizar tag en repo GitOps.
7. Argo CD Application apuntando al repo de configuración.
8. Kustomize/Helm por entorno (dev/staging/prod).
9. Secrets via External Secrets Operator o Sealed Secrets.

### Prioridad 3 — Producción

10. Autenticación (API Key / OAuth2).
11. Prometheus metrics + OpenTelemetry.
12. HPA basado en CPU/latencia.
13. NetworkPolicy y Pod Security Standards.
14. Separar `requirements-train.txt` de `requirements.txt`.

---

## 5. Cambios realizados en esta fase

### 5.1 Nuevos archivos

| Archivo | Propósito |
|---|---|
| `app/core/config.py` | Variables de entorno (`MODEL_PATH`, `PORT`, etc.) |
| `app/core/constants.py` | Constantes ML compartidas (features, versión) |
| `app/core/__init__.py` | Paquete core |
| `Dockerfile` | Imagen optimizada para producción |
| `PROJECT_AUDIT.md` | Este documento |

### 5.2 Archivos modificados

| Archivo | Cambio |
|---|---|
| `app/services/prediction_service.py` | Usa config/constants; método `is_ready()` |
| `app/api/routes/health.py` | Separación `/health` (liveness) y `/ready` (readiness) |
| `app/main.py` | Limpieza de código comentado |
| `training/train_model.py` | Genera metadata; usa constantes compartidas |
| `app/models/model_metadata.json` | Metadata enriquecida (métricas, features, timestamp) |
| `.dockerignore` | Excluye tests, training, venv, docs |
| `requirements-test.txt` | `httpx2` → `httpx==0.28.1` |
| `test/integration/test_health_endpoint.py` | Tests para `/ready` |
| `test/unit/test_prediction_service.py` | Test `is_ready()` |
| `README.md` | Instrucciones completas de ejecución |

### 5.3 Archivos eliminados

| Archivo | Motivo |
|---|---|
| `dockerfile` (minúsculas) | Reemplazado por `Dockerfile` estándar |

### 5.4 Dockerfile optimizado

- Imagen base: `python:3.12-slim-bookworm`
- Usuario non-root: `appuser`
- Variables de entorno de configuración
- Solo copia `app/` (no tests ni training)
- `HEALTHCHECK` contra `GET /health`
- `PYTHONDONTWRITEBYTECODE` y `PYTHONUNBUFFERED`

---

## 6. Verificaciones ejecutadas

| Verificación | Resultado |
|---|---|
| `python -m pytest` | ✅ 99/99 tests passed |
| API local `/health` | ✅ `{"status":"healthy"}` |
| API local `/ready` | ✅ `{"status":"ready","model_loaded":true,"model_version":"v1"}` |
| API local `/model` | ✅ Metadata correcta |
| API local `POST /predict` | ✅ Predicción numérica válida |
| `docker build` | ⚠ No ejecutado — Docker Desktop no disponible |
| Contenedor Docker | ⚠ Pendiente de verificación manual |

### Comando para verificar Docker (cuando esté disponible)

```bash
docker build -t ai-house-predictor:latest .
docker run --rm -d -p 8000:8000 --name predictor ai-house-predictor:latest
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:8000/model
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" \
  -d '{"MedInc":8.3252,"HouseAge":41.0,"AveRooms":6.9841,"AveBedrms":1.0238,"Population":322.0,"AveOccup":2.5556,"Latitude":37.88,"Longitude":-122.23}'
docker inspect --format='{{.State.Health.Status}}' predictor
docker stop predictor
```

---

## 7. Estructura MLOps propuesta (futuro)

```
App/                              # Este repositorio
├── app/                          # Solo inferencia
├── training/                     # Solo entrenamiento
├── requirements.txt              # Inferencia
├── requirements-train.txt        # Entrenamiento (futuro)
└── Dockerfile                    # Solo inferencia

mlops-gitops-config/              # Repositorio GitOps
├── base/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── configmap.yaml
├── overlays/
│   ├── dev/
│   ├── staging/
│   └── prod/
└── argocd/
    └── application.yaml

MLflow Server / Artifact Store    # Infraestructura externa
```

---

## 8. Conclusión

El proyecto **está preparado para la fase GitOps** a nivel de aplicación:

- API funcional con probes de salud.
- Configuración externalizable por variables de entorno.
- Imagen Docker orientada a producción.
- Entrenamiento e inferencia desacoplados en código y empaquetado.
- Tests automatizados completos.

**Bloqueantes restantes para GitOps real:**

1. Manifiestos Kubernetes en repositorio `Config/`.
2. Pipeline CD que actualice tags de imagen.
3. Argo CD Application configurada.
4. Estrategia de artefactos ML fuera de Git.

La siguiente fase debe implementar el repositorio de configuración GitOps y conectar el pipeline CI con Argo CD.
