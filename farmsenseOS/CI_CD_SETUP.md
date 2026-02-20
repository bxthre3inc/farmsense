# 🚀 FarmSense CI/CD Setup Guide

This guide explains how to connect your GitHub repository to your **Oracle** and **Zo.computer** instances for automated deployment.

## 1. Prepare Your Servers

On **BOTH** servers (Oracle and Zo), perform these one-time setup steps:

1. **Install Git & Docker**: Ensure git, docker, and docker-compose are installed.
2. **Clone the Repository**:

    ```bash
    cd ~
    git clone https://github.com/bxthre3/farmsense-implementation-package.git farmsense-code
    ```

    *(Note: Ensure the directory name matches `farmsense-code` as used in the workflow)*

## 2. Configure GitHub Secrets

Go to your GitHub Repository -> **Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**.

Add the following secrets:

### 🌍 Oracle Cloud (Map Stack)

| Secret Name | Value Description |
| ------------- | ------------------- |
| `ORACLE_HOST` | Public IP address of your Oracle instance |
| `ORACLE_USER` | SSH username (e.g., `ubuntu` or `opc`) |
| `ORACLE_SSH_KEY` | Private SSH Key (Content of your `.pem` file) |
| `ENV_FILE_ORACLE` | The full content of your `.env` file for Oracle. Must include: `POSTGRES_USER`, `POSTGRES_PASSWORD`, etc. |

### 🧠 Zo.computer (Core Platform)

| Secret Name | Value Description |
| ------------- | ------------------- |
| `ZO_HOST` | Public IP address of your Zo instance |
| `ZO_USER` | SSH username (e.g., `user` or `root`) |
| `ZO_SSH_KEY` | Private SSH Key |
| `ENV_FILE_ZO` | The full content of your `.env` file for Zo. |

Must include: `MAP_DATABASE_URL` pointing to Oracle IP. |

## 3. Deployment Flow

1. **Push** changes to the `main` branch.
2. **GitHub Action** triggers automatically.
3. **Job 1**: Deploys `docker-compose.oracle.yml` to Oracle.
4. **Job 2**: Deploys `docker-compose.zo.yml` to Zo (only runs if Oracle deploy succeeds).

## ⚠️ Troubleshooting

- **Permission Denied**: Ensure the SSH keys added to GitHub match the public keys in `~/.ssh/authorized_keys` on the servers.
- **Timeout**: Deployment might take time if building images from scratch. The workflow pulls changes and rebuilds.
