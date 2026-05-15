# MLOps GitOps Application

This repository contains the application layer of the TFM project:

**"Uso de GitOps para la Gobernanza de Modelos de IA en Producción (MLOps + DevOps)"**

The project focuses on the implementation of a cloud-native architecture that combines DevOps, MLOps, and GitOps practices to improve the governance, traceability, and reproducibility of Machine Learning models in production environments.

---

# Objectives

This repository is responsible for:

- Machine Learning model implementation
- API development
- Model packaging and containerization
- Continuous Integration (CI)
- Automated artifact generation
- Integration with GitOps workflows

---

# Planned Technologies

The following technologies are planned to be used during development:

- Python
- FastAPI
- Docker
- GitHub Actions
- Machine Learning libraries (scikit-learn / MLflow)
- Kubernetes
- ArgoCD

---

# Repository Structure


.
├── app/                  # Application source code
├── tests/                # Automated tests
├── models/               # ML models and artifacts
├── requirements.txt      # Python dependencies
├── Dockerfile            # Container definition
├── .github/workflows/    # GitHub Actions CI pipelines
└── README.md

---

## CI/CD

This repository will integrate Continuous Integration pipelines using GitHub Actions in order to:

·Validate source code
·Execute automated tests
·Build Docker images
·Generate deployable artifacts
·GitOps Integration

---

# GitOps Integration

The deployment configuration and Kubernetes manifests are maintained in a separate GitOps repository:

 mlops-gitops-config

This separation follows GitOps principles, using Git as the single source of truth for deployment state management.

---

# Status

Project currently under development as part of the Master's Thesis (TFM).

---

# Authors

Master's Degree in Development and Operations (DevOps)
Universidad Internacional de La Rioja (UNIR)

Rubén Cazorla Rodríguez
Cristhian Alexander Cano Correa

---