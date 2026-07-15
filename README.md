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
                         <ip>.sslip.io
                              │
                         ┌────▼─────────┐
                         │ EDGE (Caddy) │ ◄── Elastic Ip + HTTPS/TLS
                         └────┬─────────┘
                              │
              ┌───────────────────────────────┐
            /api/*                        /grafana/*
              │                               │
         ┌────▼────────┐              ┌───────▼─────┐                     
         │   API EC2   │              │ Grafana EC2 │ 
         └────┬────────┘              └─────────────┘     
              │
              │
        ┌─────┼────────┼───────────────┬──────────────┐
        ▼              ▼               ▼              ▼
  RDS PostgreSQL   Amazon S3      DynamoDB        ECR (imagem)
  (tarefas)        (uploads)      (eventos/logs)  (Repositório de Imagens)

  Infra descrita como código (CDK): S3, ECR, VPC  →  reprodutível e versionada.
```

## Tecnologias utilizadas
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Docker
- Amazon ECR
- Amazon EKS
- Kubernetes
- Amazon S3
- Amazon RDS
- Amazon DynamoDB
- Grafana
- AWS CDK
- Amazon CloudWatch

## Endpoints

| Método | Caminho               | Descrição |
| ------ | --------------------- | --------- |
| GET    | `/`                   | Metadados da aplicação. |
| GET    | `/health`             | Liveness probe. |
| GET    | `/health/ready`       | Readiness (checa o PostgreSQL). |
| POST   | `/tasks`              | Criar tarefa (201). |
| GET    | `/tasks`              | Listar (paginação `skip`/`limit`). |
| GET    | `/tasks/{task_id}`    | Obter por id (404). |
| PUT    | `/tasks/{task_id}`    | Atualizar parcial. |
| DELETE | `/tasks/{task_id}`    | Remover (204). |
| **POST** | **`/uploads`**          | **Enviar arquivo (multipart, 201)** |
| **GET**  | **`/uploads/{filename}`** | **Baixar (200) ou redirect S3 (307)** |
| GET    | `/docs`               | Swagger UI. |

## Estrutura final do projeto 
```text
cloudtask-ai-saas/
├── app/
│   ├── main.py
│   ├── core/            # config, security
│   ├── api/             # routes_health, routes_tasks, routes_uploads, routes_events
│   ├── db/              # database, models, schemas
│   ├── services/        # s3_service, dynamodb_service, task_service
│   └── utils/           # logging
├── infra/
│   ├── docker/
│   ├── k8s/             # local + aws/
│   └── cdk/             # stacks S3, ECR, VPC
├── scripts/             # build-and-push-ecr.sh, load-test
├── tests/
├── docs/                # ROADMAP, HOW_TO_USE, arquitetura, LGPD, etc.
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Infraestrutura como Código com AWS CDK

### 1. Clonar o projeto
Clone o repositório do GitHub ou faça o download do projeto em formato .zip.
```text
git clone https://github.com/SEU-USUARIO/cloudtask-ai-saas.git
cd cloudtask-ai-saas
```
### 2. Abrir o projeto no Dev Container
Abra o projeto no Visual Studio Code e selecione a opção **Reopen in Container** para iniciar o ambiente de desenvolvimento configurado.

### 3. Verificar a autenticação na AWS
Confirme que o ambiente está autenticado na conta da AWS executando:
```text
aws sts get-caller-identity
```
> **O comando deverá retornar informações como Account, Arn e UserId, indicando que as credenciais estão configuradas corretamente.**

### 4. Acessar a pasta do AWS CDK
```text
cd infra/cdk
```

### 3. Verificar se o AWS CDK está instalado
Execute o comando abaixo para confirmar que a biblioteca **aws-cdk-lib** está instalada e disponível no ambiente Python.
```text
python3 -c "import aws_cdk; print('aws-cdk-lib OK')"
```
> **este comando apenas verifica a instalação da biblioteca e não cria nem modifica recursos na AWS.**
> **Se tudo estiver correto, será exibida a mensagem: aws-cdk-lib OK**

### 6. Executar o deploy da infraestrutura
Ainda na pasta infra/cdk, execute:
```text
./cdk-deploy.sh deploy
```
#### O script realiza automaticamente as seguintes etapas

  - verifica as dependências do projeto; 
  - executa o cdk synth; 
  - cria ou atualiza as stacks da infraestrutura na AWS;
  - exibe os endereços da API (Swagger) e do Grafana ao final do deploy.

### 7. Remover a infraestrutura 
Após concluir os testes, remova todos os recursos criados na AWS utilizando:
```text
./cdk-deploy.sh destroy
```
> **Este comando remove as stacks provisionadas pelo AWS CDK, evitando custos desnecessários**

## Licença
Projeto desenvolvido exclusivamente para fins acadêmicos.
