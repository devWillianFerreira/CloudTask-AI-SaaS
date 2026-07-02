#!/bin/bash
# =============================================================================
# user-data do servidor de API (EC2) — Aula 12
# -----------------------------------------------------------------------------
# Sobe a API CloudTask num EC2 Amazon Linux 2023:
#   * instala Docker + git;
#   * clona o repositório (branch da Semana 6);
#   * sobe um PostgreSQL e a API em containers, na mesma rede Docker;
#   * a API fica exposta na porta 8000.
#
# POR QUÊ Postgres em container aqui: este é o caminho "rápido/barato" do script
# CLI (VPC default, sem RDS). No caminho CDK de produção, o mesmo user-data
# recebe DATABASE_URL apontando para o RDS (ver ComputeStack) e NÃO sobe o
# container de banco. Tudo é controlado pelas variáveis abaixo.
#
# Variáveis que o lançador injeta no topo deste script (export ...):
#   ADMIN_PASSWORD   senha do admin da API/app   (default admin#123)
#   SECRET_KEY       chave de assinatura do JWT   (TROCAR em produção)
#   DATABASE_URL     se vier preenchida, usa esse banco (ex.: RDS) e NÃO sobe o
#                    container `db`. Se vazia, sobe Postgres local em container.
#   REPO_URL / BRANCH  origem do código.
# =============================================================================
set -xe

: "${ADMIN_PASSWORD:=admin#123}"
: "${SECRET_KEY:=demo-troque-em-producao}"
: "${REPO_URL:=https://github.com/N-CPUninter/Computa-o-em-Nuvem---Projeto-exemplo-CloudTask-AI-SaaS.git}"
: "${BRANCH:=semana-06-cdk-final}"
: "${DATABASE_URL:=}"
: "${ROOT_PATH:=}"   # atrás do proxy: "/api" (Swagger gera URLs com o prefixo)
# Storage dos uploads: o lançador escolhe. Sem export = modo local (disco do
# container, efêmero). O caminho CDK exporta STORAGE_MODE=s3 + S3_BUCKET_NAME
# (nome do bucket resolvido em deploy time pelo CloudFormation).
: "${STORAGE_MODE:=local}"        # local | s3
: "${AWS_REGION:=us-east-1}"
: "${S3_BUCKET_NAME:=}"
: "${S3_PRESIGNED_URL_EXPIRES:=3600}"

dnf update -y
dnf install -y docker git
systemctl enable --now docker

cd /opt
git clone --depth 1 -b "$BRANCH" "$REPO_URL" app
cd app

docker network create cloudtask || true

# Banco: usa RDS (DATABASE_URL externa) OU sobe Postgres local em container.
if [ -z "$DATABASE_URL" ]; then
  docker run -d --name db --network cloudtask --restart unless-stopped \
    -e POSTGRES_USER=cloudtask -e POSTGRES_PASSWORD=cloudtask -e POSTGRES_DB=cloudtask \
    -v pgdata:/var/lib/postgresql/data postgres:16
  DATABASE_URL="postgresql+psycopg2://cloudtask:cloudtask@db:5432/cloudtask"
  # espera o banco aceitar conexões
  for i in $(seq 1 30); do
    docker exec db pg_isready -U cloudtask && break
    sleep 2
  done
fi

# Imagem da API (target prod do Dockerfile do repo).
docker build -t cloudtask-api:prod --target prod .

# ANTES o storage era fixo no modo local:  -e STORAGE_MODE=local
# AGORA vem das variáveis (default `local`); o caminho CDK exporta STORAGE_MODE=s3
# + S3_BUCKET_NAME e a API grava no S3. (Comentários não podem ir DENTRO do
# `docker run ... \` — quebram a continuação de linha; por isso ficam aqui.)
docker run -d --name api --network cloudtask --restart unless-stopped \
  -p 8000:8000 \
  -e APP_ENV=production \
  -e LOG_LEVEL=INFO \
  -e DATABASE_URL="$DATABASE_URL" \
  -e SECRET_KEY="$SECRET_KEY" \
  -e ADMIN_USERNAME=admin \
  -e ADMIN_PASSWORD="$ADMIN_PASSWORD" \
  -e STORAGE_MODE="$STORAGE_MODE" \
  -e AWS_REGION="$AWS_REGION" \
  -e S3_BUCKET_NAME="$S3_BUCKET_NAME" \
  -e S3_PRESIGNED_URL_EXPIRES="$S3_PRESIGNED_URL_EXPIRES" \
  -e CORS_ORIGINS='*' \
  -e ROOT_PATH="$ROOT_PATH" \
  cloudtask-api:prod

echo "API up on :8000"