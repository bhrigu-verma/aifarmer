# Deployment Guide — AI Farmer Assistant

Step-by-step instructions for deploying the backend to AWS Mumbai region and submitting the Android app to Google Play Store.

---

## Table of Contents

- [Backend Deployment (AWS Mumbai)](#backend-deployment-aws-mumbai)
  - [Infrastructure Overview](#infrastructure-overview)
  - [Prerequisites](#prerequisites)
  - [Step 1: Provision AWS Resources](#step-1-provision-aws-resources)
  - [Step 2: Configure the Database](#step-2-configure-the-database)
  - [Step 3: Deploy the Application](#step-3-deploy-the-application)
  - [Step 4: Configure Domain and SSL](#step-4-configure-domain-and-ssl)
  - [Step 5: Set Up Monitoring](#step-5-set-up-monitoring)
- [Play Store Submission](#play-store-submission)
- [CI/CD Pipeline](#cicd-pipeline)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

---

## Backend Deployment (AWS Mumbai)

### Infrastructure Overview

```
                        Internet
                           │
                    ┌──────▼──────┐
                    │ CloudFront  │  (CDN + SSL termination)
                    │ + ACM cert  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   ALB       │  (Application Load Balancer)
                    │ ap-south-1  │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼─────┐┌────▼─────┐┌────▼─────┐
        │ ECS Task  ││ ECS Task ││ ECS Task │  (Fargate containers)
        │ (FastAPI) ││ (FastAPI)││ (FastAPI) │
        └─────┬─────┘└────┬─────┘└────┬─────┘
              │            │            │
              └────────────┼────────────┘
                           │
                    ┌──────▼──────┐
                    │   RDS       │  (PostgreSQL 15)
                    │ db.t3.micro │
                    │ Multi-AZ    │
                    └─────────────┘

Region: ap-south-1 (Mumbai)
Reason: Lowest latency for Indian users (~20-50ms)
```

### Why Mumbai Region

| Factor | Benefit |
|--------|---------|
| **Latency** | 20–50ms to most Indian cities (vs 150–200ms from US/EU) |
| **Data residency** | Farmer data stays in India (compliance with potential data localization laws) |
| **Cost** | Competitive pricing, ₹ billing available |
| **Availability** | 3 Availability Zones for high availability |

### Prerequisites

- AWS account with IAM admin access
- AWS CLI v2 installed and configured
- Docker installed locally
- Domain name (e.g., `api.aifarmer.in`)
- Python 3.11+ (for local testing)

### Step 1: Provision AWS Resources

#### 1.1 VPC and Networking

```bash
# Create VPC with public and private subnets
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --region ap-south-1 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=aifarmer-vpc}]'

# Create subnets (2 public for ALB, 2 private for ECS/RDS)
# Public subnets: 10.0.1.0/24 (ap-south-1a), 10.0.2.0/24 (ap-south-1b)
# Private subnets: 10.0.3.0/24 (ap-south-1a), 10.0.4.0/24 (ap-south-1b)
```

#### 1.2 Security Groups

```bash
# ALB Security Group - allow HTTP/HTTPS from internet
aws ec2 create-security-group --group-name aifarmer-alb-sg \
  --description "ALB security group" --vpc-id <vpc-id>
aws ec2 authorize-security-group-ingress --group-id <alb-sg-id> \
  --protocol tcp --port 443 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id <alb-sg-id> \
  --protocol tcp --port 80 --cidr 0.0.0.0/0

# ECS Security Group - allow traffic from ALB only
aws ec2 create-security-group --group-name aifarmer-ecs-sg \
  --description "ECS tasks security group" --vpc-id <vpc-id>
aws ec2 authorize-security-group-ingress --group-id <ecs-sg-id> \
  --protocol tcp --port 8000 --source-group <alb-sg-id>

# RDS Security Group - allow traffic from ECS only
aws ec2 create-security-group --group-name aifarmer-rds-sg \
  --description "RDS security group" --vpc-id <vpc-id>
aws ec2 authorize-security-group-ingress --group-id <rds-sg-id> \
  --protocol tcp --port 5432 --source-group <ecs-sg-id>
```

#### 1.3 RDS PostgreSQL

```bash
aws rds create-db-instance \
  --db-instance-identifier aifarmer-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.4 \
  --master-username aifarmer_admin \
  --master-user-password <SECURE_PASSWORD> \
  --allocated-storage 20 \
  --storage-type gp3 \
  --vpc-security-group-ids <rds-sg-id> \
  --db-subnet-group-name aifarmer-db-subnet \
  --multi-az \
  --backup-retention-period 7 \
  --region ap-south-1
```

**RDS Configuration:**

| Setting | Value | Reason |
|---------|-------|--------|
| Instance class | db.t3.micro | Cost-effective for initial launch (2 vCPU, 1 GB RAM) |
| Storage | 20 GB gp3 | Sufficient for 100K farmers' data |
| Multi-AZ | Yes | High availability |
| Backup retention | 7 days | Recovery from data issues |
| Engine | PostgreSQL 15 | Mature, JSON support, full-text search |

### Step 2: Configure the Database

#### 2.1 Connect and Initialize

```bash
# Connect to RDS
psql -h aifarmer-db.xxxxx.ap-south-1.rds.amazonaws.com \
  -U aifarmer_admin -d postgres

# Create database
CREATE DATABASE aifarmer;
\c aifarmer

# Run Alembic migrations
cd backend
DATABASE_URL="postgresql://aifarmer_admin:<password>@<rds-endpoint>:5432/aifarmer" \
  alembic upgrade head
```

#### 2.2 Seed Initial Data

```bash
# Load crop data, MSP rates, scheme information
DATABASE_URL="postgresql://..." python -c "
from app.models.database import create_tables
create_tables()
print('Tables created successfully')
"
```

### Step 3: Deploy the Application

#### 3.1 Create Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### 3.2 Build and Push to ECR

```bash
# Create ECR repository
aws ecr create-repository --repository-name aifarmer-backend --region ap-south-1

# Login to ECR
aws ecr get-login-password --region ap-south-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-south-1.amazonaws.com

# Build and push
docker build -t aifarmer-backend ./backend
docker tag aifarmer-backend:latest <account-id>.dkr.ecr.ap-south-1.amazonaws.com/aifarmer-backend:latest
docker push <account-id>.dkr.ecr.ap-south-1.amazonaws.com/aifarmer-backend:latest
```

#### 3.3 ECS Fargate Setup

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name aifarmer-cluster --region ap-south-1

# Register task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create service
aws ecs create-service \
  --cluster aifarmer-cluster \
  --service-name aifarmer-api \
  --task-definition aifarmer-backend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[<private-subnet-1>,<private-subnet-2>],securityGroups=[<ecs-sg-id>]}" \
  --load-balancers "targetGroupArn=<target-group-arn>,containerName=aifarmer-backend,containerPort=8000"
```

**ECS Task Definition** (`ecs-task-definition.json`):

```json
{
  "family": "aifarmer-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "aifarmer-backend",
      "image": "<account-id>.dkr.ecr.ap-south-1.amazonaws.com/aifarmer-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "DATABASE_URL", "value": "postgresql://..."},
        {"name": "APP_ENV", "value": "production"},
        {"name": "SECRET_KEY", "value": "..."}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/aifarmer-backend",
          "awslogs-region": "ap-south-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 10,
        "retries": 3
      }
    }
  ]
}
```

### Step 4: Configure Domain and SSL

#### 4.1 ACM Certificate

```bash
# Request SSL certificate
aws acm request-certificate \
  --domain-name api.aifarmer.in \
  --validation-method DNS \
  --region ap-south-1
```

#### 4.2 ALB Configuration

```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name aifarmer-alb \
  --subnets <public-subnet-1> <public-subnet-2> \
  --security-groups <alb-sg-id> \
  --type application \
  --region ap-south-1

# Create target group
aws elbv2 create-target-group \
  --name aifarmer-api-tg \
  --protocol HTTP \
  --port 8000 \
  --target-type ip \
  --vpc-id <vpc-id> \
  --health-check-path /health

# Create HTTPS listener
aws elbv2 create-listener \
  --load-balancer-arn <alb-arn> \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=<acm-cert-arn> \
  --default-actions Type=forward,TargetGroupArn=<target-group-arn>

# HTTP → HTTPS redirect
aws elbv2 create-listener \
  --load-balancer-arn <alb-arn> \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=redirect,RedirectConfig='{Protocol=HTTPS,Port=443,StatusCode=HTTP_301}'
```

#### 4.3 Route 53 DNS

```bash
# Create A record pointing to ALB
aws route53 change-resource-record-sets \
  --hosted-zone-id <zone-id> \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.aifarmer.in",
        "Type": "A",
        "AliasTarget": {
          "DNSName": "<alb-dns-name>",
          "HostedZoneId": "<alb-hosted-zone-id>",
          "EvaluateTargetHealth": true
        }
      }
    }]
  }'
```

### Step 5: Set Up Monitoring

#### 5.1 CloudWatch Alarms

```bash
# API error rate alarm (>5% 5xx errors)
aws cloudwatch put-metric-alarm \
  --alarm-name aifarmer-api-errors \
  --metric-name HTTPCode_Target_5XX_Count \
  --namespace AWS/ApplicationELB \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions <sns-topic-arn>

# Database CPU alarm (>80%)
aws cloudwatch put-metric-alarm \
  --alarm-name aifarmer-db-cpu \
  --metric-name CPUUtilization \
  --namespace AWS/RDS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 3 \
  --alarm-actions <sns-topic-arn>
```

#### 5.2 Application Logging

```bash
# Create CloudWatch log group
aws logs create-log-group \
  --log-group-name /ecs/aifarmer-backend \
  --retention-in-days 30 \
  --region ap-south-1
```

#### 5.3 Health Check Endpoint

The app exposes `GET /health` which returns:

```json
{
  "status": "healthy",
  "app": "AI Farmer Assistant",
  "version": "1.0.0"
}
```

Used by ALB target group health checks (every 30 seconds).

---

## Play Store Submission

### Prerequisites

| Requirement | Details |
|-------------|---------|
| Google Play Developer Account | $25 one-time fee ([play.google.com/console](https://play.google.com/console)) |
| Android App Bundle (.aab) | Signed release build |
| Privacy Policy URL | Hosted on website (required for apps collecting personal data) |
| App Icon | 512×512 PNG (no transparency) |
| Feature Graphic | 1024×500 PNG |
| Screenshots | Min 2 per device type (phone, tablet) — 320px min width |
| Target API Level | API 34+ (Android 14) for new submissions in 2024 |

### Store Listing Details

```yaml
App Name: AI Farmer Assistant - कृषि सहायक
Short Description (80 chars): 
  "Smart farming app: crop advice, mandi prices, weather alerts in Hindi"

Full Description:
  "AI Farmer Assistant helps Indian farmers make better decisions throughout 
  the farming season. Get personalized crop recommendations based on your 
  soil type, real-time mandi prices from 7000+ markets, 10-day weather 
  forecasts with crop-specific alerts, and track your expenses with our 
  crop diary.

  Features:
  • Crop Advisor: Personalized recommendations based on your soil, season, and location
  • Mandi Prices: Daily prices from your nearest mandis with sell/wait advice
  • Weather Alerts: 10-day forecast with frost, rain, and heat wave warnings
  • Disease Detection: Photograph crop diseases for instant identification
  • Crop Diary: Track expenses, income, and calculate profit per season
  • Government Schemes: Check eligibility for PM-KISAN, PMFBY, KCC, and more
  • Works Offline: All features work without internet

  Available in Hindi, English, Marathi, Tamil, Telugu, Kannada, Bengali, 
  Gujarati, Punjabi, and Malayalam."

Category: Tools (or Productivity)
Content Rating: Everyone
Price: Free
```

### App Signing

```bash
# Generate release keystore (do this ONCE, keep it secure)
keytool -genkey -v -keystore aifarmer-release.keystore \
  -alias aifarmer -keyalg RSA -keysize 2048 -validity 10000

# Build release AAB (Android App Bundle)
cd android
./gradlew bundleRelease

# The signed AAB will be at:
# android/app/build/outputs/bundle/release/app-release.aab
```

### Submission Checklist

- [ ] **App Bundle**: Signed `.aab` file uploaded
- [ ] **Store Listing**: Title, description, screenshots in Hindi + English
- [ ] **Content Rating**: IARC questionnaire completed
- [ ] **Privacy Policy**: URL provided (must cover farmer data collection, location, camera permissions)
- [ ] **Target API**: Set to API 34 (Android 14)
- [ ] **Permissions Declaration**: Camera (disease detection), Location (weather), Internet (sync)
- [ ] **Data Safety Section**: Declare what data is collected and how it's used
- [ ] **App Review**: Initial review takes 3-7 days for new developers

### Data Safety Declaration

| Data Type | Collected | Shared | Purpose |
|-----------|-----------|--------|---------|
| Name | Yes | No | Account personalization |
| Phone number | Yes | No | Account identification |
| Location (precise) | Yes | No | Weather forecasts, nearest mandis |
| Photos | Yes | No | Disease detection (processed on-device) |
| Financial info (expenses) | Yes | No | Crop diary, profit tracking |
| App activity | Yes | No | Analytics, feature improvement |

### Permissions Required

| Permission | Android Manifest | Reason |
|------------|-----------------|--------|
| `INTERNET` | Normal | API calls, data sync |
| `ACCESS_NETWORK_STATE` | Normal | Check connectivity for sync |
| `CAMERA` | Dangerous | Crop disease photo capture |
| `ACCESS_FINE_LOCATION` | Dangerous | GPS for weather and mandi |
| `ACCESS_COARSE_LOCATION` | Dangerous | Fallback location |
| `READ_EXTERNAL_STORAGE` | Dangerous | Select existing photos |

---

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: |
          cd backend
          pip install -r requirements.txt
          pytest tests/ -v

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-south-1

      - name: Login to ECR
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push Docker image
        run: |
          docker build -t aifarmer-backend ./backend
          docker tag aifarmer-backend:latest ${{ secrets.ECR_REGISTRY }}/aifarmer-backend:latest
          docker push ${{ secrets.ECR_REGISTRY }}/aifarmer-backend:latest

      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster aifarmer-cluster \
            --service aifarmer-api \
            --force-new-deployment
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | `sqlite:///./aifarmer.db` | PostgreSQL connection string for production |
| `SECRET_KEY` | Yes | `dev-secret-key-change-in-production` | JWT signing key (change in production!) |
| `APP_ENV` | No | `development` | Environment: development / staging / production |
| `IMD_API_URL` | No | `https://api.open-meteo.com/v1/forecast` | Weather API endpoint |
| `AGMARKNET_BASE_URL` | No | `https://agmarknet.gov.in` | Mandi price scraping target |
| `ALGORITHM` | No | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `43200` | JWT token expiry (30 days) |
| `LOG_LEVEL` | No | `INFO` | Logging level |

### Production Secrets (use AWS Secrets Manager or SSM Parameter Store)

```bash
# Store secrets in AWS SSM
aws ssm put-parameter --name "/aifarmer/prod/database-url" \
  --type SecureString --value "postgresql://..." --region ap-south-1

aws ssm put-parameter --name "/aifarmer/prod/secret-key" \
  --type SecureString --value "<random-256-bit-key>" --region ap-south-1
```

---

## Troubleshooting

### Common Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| 502 Bad Gateway | ECS task not healthy | Check CloudWatch logs: `/ecs/aifarmer-backend` |
| Database connection timeout | Security group misconfigured | Ensure ECS SG can reach RDS SG on port 5432 |
| Slow API responses | Database queries not optimized | Check slow query logs; add missing indexes |
| Health check failing | App startup error | Check container logs; verify env variables |
| Image upload timeout | ALB timeout too low | Increase ALB idle timeout to 120s |

### Useful Commands

```bash
# View ECS service status
aws ecs describe-services --cluster aifarmer-cluster --services aifarmer-api

# View recent logs
aws logs tail /ecs/aifarmer-backend --since 1h --follow

# Force redeploy
aws ecs update-service --cluster aifarmer-cluster --service aifarmer-api --force-new-deployment

# Check RDS status
aws rds describe-db-instances --db-instance-identifier aifarmer-db

# Run database migrations on production
docker run --rm -e DATABASE_URL="postgresql://..." aifarmer-backend:latest \
  alembic upgrade head
```

### Scaling Guidelines

| Metric | Threshold | Action |
|--------|-----------|--------|
| CPU utilization > 70% | Sustained 5 min | Scale ECS tasks from 2 → 4 |
| Response time > 500ms (p95) | Sustained 10 min | Check database, add read replicas |
| Database connections > 80% | Sustained 5 min | Increase connection pool or upgrade instance |
| Storage > 80% | — | Increase RDS allocated storage |
| 10K+ concurrent users | — | Add ElastiCache (Redis) for price/weather caching |
