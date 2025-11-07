# Jenkins CI/CD Pipeline Configuration Guide

This guide explains how to configure the Jenkins CI/CD pipeline for automatic deployment to your EC2 instance.

## Prerequisites

1. **Jenkins Instance**: Running Jenkins on EC2 with necessary plugins installed
2. **EC2 App Instance**: Your application EC2 instance with:
   - Docker and Docker Compose installed
   - SSH access configured
   - Required ports open (5001 for the app)
   - Access to RDS database via proxy
3. **RDS Database**: PostgreSQL database on AWS RDS with proxy endpoint
4. **Jenkins Plugins**: Ensure these plugins are installed:
   - SSH Agent Plugin
   - Pipeline Plugin
   - Git Plugin

## Configuration Steps

### 1. Configure Jenkins Credentials

#### SSH Key for EC2 Access

1. Go to **Jenkins Dashboard** → **Manage Jenkins** → **Credentials** → **System** → **Global credentials**
2. Click **Add Credentials**
3. Configure:
   - **Kind**: SSH Username with private key
   - **ID**: `pfm-ec2-ssh-key` (must match the ID in Jenkinsfile)
   - **Username**: Your EC2 username (usually `ubuntu` or `ec2-user`)
   - **Private Key**: Enter directly or upload your SSH private key file
   - **Description**: "SSH key for EC2 app instance"

#### Production Environment Variables

Create the following **Secret text** credentials in Jenkins (these will be used by the pipeline):

1. **Database URL** (RDS via Proxy):
   - **ID**: `pfm-database-url`
   - **Kind**: Secret text
   - **Secret**: Your RDS database connection string
     - Format: `postgresql+psycopg2://username:password@rds-proxy-endpoint:port/dbname`
     - Example: `postgresql+psycopg2://myuser:mypass@my-rds-proxy.region.rds.amazonaws.com:5432/mydb`

2. **Secret Key**:
   - **ID**: `pfm-secret-key`
   - **Kind**: Secret text
   - **Secret**: Your Flask secret key (generate a strong random key)

3. **Flask Environment** (Optional):
   - **ID**: `pfm-flask-env`
   - **Kind**: Secret text
   - **Secret**: `production` (defaults to `production` if not set)

4. **Seed Predefined** (Optional):
   - **ID**: `pfm-seed-predefined`
   - **Kind**: Secret text
   - **Secret**: `0` (defaults to `0` if not set)

#### EC2 Connection Details

Set these as environment variables in Jenkins job configuration or as pipeline parameters:
- `EC2_HOST`: Your EC2 instance IP or hostname (required)
- `EC2_USER`: Your EC2 username (optional, defaults to `ubuntu`)

### 2. Configure Jenkins Pipeline

#### Option A: Using Environment Variables (Recommended)

1. Go to your Jenkins job configuration
2. Navigate to **Build Environment** section
3. Check **Use secret text(s) or file(s)**
4. Add bindings:
   - **Variable**: `EC2_HOST`
   - **Credentials**: Create a secret text credential with your EC2 instance IP/hostname
   - **Variable**: `EC2_USER` (optional, defaults to `ubuntu`)
   - **Credentials**: Create a secret text credential with your EC2 username

#### Option B: Using Pipeline Parameters

Modify the Jenkinsfile to accept parameters:

```groovy
parameters {
    string(name: 'EC2_HOST', defaultValue: '', description: 'EC2 instance hostname or IP')
    string(name: 'EC2_USER', defaultValue: 'ubuntu', description: 'EC2 username')
}
```

### 3. Configure EC2 Instance

#### Initial Setup on EC2

SSH into your EC2 instance and run:

```bash
# Install Docker (if not already installed)
sudo apt-get update
sudo apt-get install -y docker.io docker-compose curl

# Add your user to docker group (if needed)
sudo usermod -aG docker $USER

# Log out and back in for group changes to take effect
# Or run: newgrp docker

# Create deployment directory
sudo mkdir -p /opt/pfm
sudo chown $USER:$USER /opt/pfm

# Verify Docker is working
docker --version
docker-compose --version
```

**Note**: Environment variables are now managed through Jenkins credentials and will be passed to Docker containers during deployment. No `.env` file is needed on the EC2 instance.

#### Security Group Configuration

Ensure your EC2 security group allows:
- **Inbound SSH (22)**: From Jenkins instance IP
- **Inbound HTTP (5001)**: From your access IP or 0.0.0.0/0 if public
- **Outbound**: All traffic (for pulling Docker images and connecting to RDS)

#### RDS Proxy Configuration

Ensure your EC2 instance can connect to RDS via the proxy:
- EC2 security group must allow outbound connections to RDS proxy endpoint
- RDS proxy security group must allow inbound from EC2 security group
- Verify network connectivity: `telnet rds-proxy-endpoint 5432`

### 4. Configure Webhook (if using GitHub/GitLab)

1. Go to your repository settings
2. Navigate to **Webhooks**
3. Add webhook:
   - **Payload URL**: `http://your-jenkins-ip:8080/github-webhook/` (or GitLab equivalent)
   - **Content type**: `application/json`
   - **Events**: Select "Push events" and filter for `main` branch only

### 5. Test the Pipeline

1. Make a small change to your `main` branch
2. Push to trigger the webhook
3. Monitor the Jenkins build console for any errors
4. Verify deployment by accessing your app at `http://your-ec2-ip:5001`

## Pipeline Stages

The pipeline consists of the following stages:

1. **Checkout**: Verifies branch and checks out code from `main` branch
2. **Test**: Runs pytest test suite (must pass before deployment)
3. **Build**: Builds Docker image for production
4. **Deploy to EC2**: 
   - Creates backup of current deployment
   - Syncs files to EC2 (excluding unnecessary files)
   - Retrieves environment variables from Jenkins credentials
   - Stops old containers gracefully
   - Builds and starts new containers with production environment variables
   - Runs database migrations
   - Performs health check (30 retries, 2-second intervals)

## Deployment Directory

The application is deployed to `/opt/pfm` on the EC2 instance.

## Troubleshooting

### Common Issues

#### SSH Connection Failed
- Verify SSH key is correctly configured in Jenkins
- Check EC2 security group allows SSH from Jenkins IP
- Test SSH connection manually: `ssh -i your-key.pem user@ec2-ip`

#### Docker Permission Denied
- Ensure user is in docker group: `sudo usermod -aG docker $USER`
- Log out and back in, or restart SSH session

#### Health Check Fails
- Check application logs: `docker-compose -f docker-compose.prod.yml logs`
- Verify port 5001 is accessible
- Check database connection in .env file

#### Environment Variables Not Loading
- Verify Jenkins credentials are correctly configured with IDs:
  - `prod-database-url`
  - `prod-secret-key`
  - `prod-flask-env` (optional)
  - `prod-seed-predefined` (optional)
- Check Jenkins build console for credential errors
- Verify DATABASE_URL format matches: `postgresql+psycopg2://user:pass@host:port/dbname`

#### RDS Connection Issues
- Verify EC2 security group allows outbound to RDS proxy
- Check RDS proxy security group allows inbound from EC2
- Test connection manually: `psql -h rds-proxy-endpoint -U username -d dbname`
- Verify DATABASE_URL in Jenkins credentials uses the proxy endpoint, not direct RDS endpoint

### Viewing Logs

On EC2 instance:
```bash
cd /opt/pfm
docker-compose -f docker-compose.prod.yml logs -f

# View only web container logs
docker-compose -f docker-compose.prod.yml logs -f web

# View last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100
```

## Best Practices Implemented

✅ **Branch Protection**: Only deploys from `main` branch  
✅ **Automated Testing**: Runs tests before deployment (fails pipeline if tests fail)  
✅ **Backup Strategy**: Creates backups before deployment  
✅ **Health Checks**: Verifies deployment success with retry logic  
✅ **Rollback Capability**: Backups enable quick rollback  
✅ **Clean Builds**: Uses `--no-cache` for fresh builds  
✅ **Resource Management**: Cleans up old Docker images  
✅ **Error Handling**: Proper error handling and logging  
✅ **Idempotent Deployments**: Can be run multiple times safely  
✅ **Secure Credentials**: Environment variables stored in Jenkins credentials (not in code)  
✅ **RDS Integration**: Uses RDS proxy for database connections (no local database container)  
✅ **Production Ready**: Separate production docker-compose configuration  

## Security Recommendations

1. **Jenkins Credentials**: Environment variables stored securely in Jenkins (implemented)
2. **Restrict SSH access** to Jenkins instance IP only
3. **Use HTTPS** for production (consider adding nginx reverse proxy)
4. **Rotate secrets** regularly (especially SECRET_KEY and database passwords)
5. **Enable CloudWatch** logging for EC2 instance
6. **Use IAM roles** for EC2 instances instead of access keys
7. **Enable MFA** for Jenkins admin access
8. **RDS Proxy**: Use RDS proxy for connection pooling and enhanced security (implemented)
9. **Network Security**: Ensure EC2 and RDS are in private subnets with proper security groups
10. **Regular Updates**: Keep Docker images and EC2 instances updated with security patches

## Optional Enhancements

### Add Slack/Email Notifications

Uncomment and configure notification lines in Jenkinsfile:
```groovy
// slackSend(color: 'good', message: "Deployment successful: ${env.BUILD_URL}")
```

### Enable Automatic Rollback

Uncomment rollback logic in the failure post-action.

### Add Blue-Green Deployment

For zero-downtime deployments, consider implementing blue-green deployment strategy.

### Add Database Migration Scripts

For production, consider using Alembic or similar migration tool instead of `db.create_all()`.

