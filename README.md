<div align="center" style="background-color: white; max-width: 70%;">
  <img alt="BANNER do repositório CloudTask AI SaaS — disciplina Computação em Nuvem" title="Banner_CloudTask_AI_SaaS" src="https://raw.githubusercontent.com/N-CPUninter/Computa-o-em-Nuvem---Projeto-exemplo-CloudTask-AI-SaaS/refs/heads/semana-02-rds-vpc-seguranca/.readme_docs/Banner_Github_NCPU.png" width="100%" />
</div>
<div align="center">
  <h1>CloudTask AI SaaS</h1>
  <p>O CloudTask AI SaaS é uma API REST desenvolvida em FastAPI para gerenciamento de tarefas.</p>
  <p>Durante a disciplina o projeto evoluiu desde uma aplicação local utilizando Docker até uma infraestrutura completa na AWS, incluindo Kubernetes, armazenamento em nuvem, banco de dados gerenciado, monitoramento e Infraestrutura como Código utilizando AWS CDK.</p>
</div>

<p align="center">
  <a href="https://www.python.org/" title="Python"><img src="https://github.com/get-icon/geticon/raw/master/icons/python.svg" alt="Python" height="21px"></a>
  +
  <a href="https://fastapi.tiangolo.com/" title="FastAPI"><img src="https://icon.icepanel.io/Technology/svg/FastAPI.svg" alt="FastAPI" height="21px"></a>
  +
  <a href="https://www.docker.com/" title="Docker"><img src="https://github.com/get-icon/geticon/raw/master/icons/docker-icon.svg" alt="Docker" height="21px"></a>
  +
  <a href="https://www.postgresql.org/" title="PostgreSQL"><img src="https://github.com/get-icon/geticon/raw/master/icons/postgresql.svg" alt="PostgreSQL" height="21px"></a>
  +
  <a href="https://aws.amazon.com/s3/" title="Amazon S3">Amazon S3</a>
  +
  <a href="https://kubernetes.io/" title="Kubernetes">Kubernetes</a>
  +
  <a href="https://aws.amazon.com/ecr/" title="Amazon ECR">Amazon ECR</a>
  +
  <a href="https://aws.amazon.com/eks/" title="Amazon EKS">Amazon EKS</a>
  +
  <a href="https://aws.amazon.com/cdk/" title="AWS CDK">AWS CDK</a>
</p>

## Arquitetura do Projeto

```text
                         Internet (HTTPS)
                              │
                       www.seu-dominio  ── Route 53 (DNS)
                              │
                         ┌────▼─────┐
                         │   ALB    │ ◄── ACM (certificado TLS)
                         └────┬─────┘
                  TLS termina aqui; HTTP interno
                              │
              ┌───────────────▼────────────────┐
              │        Amazon EKS (cluster)     │
              │   ┌──────────┐   HPA 2..5       │
              │   │ Pods API │ ◄── escala c/ CPU│
              │   └────┬─────┘                  │
              └────────┼───────────────────────┘
                       │
        ┌──────────────┼───────────────┬──────────────┐
        ▼              ▼               ▼              ▼
  RDS PostgreSQL   Amazon S3      DynamoDB        ECR (imagem)
  (tarefas)        (uploads)      (eventos/logs)  (origem do deploy)

  Infra descrita como código (CDK): S3, ECR, VPC  →  reprodutível e versionada.
```


