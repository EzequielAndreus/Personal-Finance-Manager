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

The pipeline uses a **parameter-based approach** where credentials are selected at build time through pipeline parameters. You need to create the following credentials in Jenkins, which will be referenced by their credential IDs when running the pipeline.

#### Create Required Credentials

Go to **Jenkins Dashboard** → **Manage Jenkins** → **Credentials** → **System** → **Global credentials** and create the following:

1. **SSH Private Key** (for EC2 access):
   - **Kind**: SSH Username with private key
   - **ID**: Choose any ID (e.g., `ec2-ssh-key`)
   - **Username**: Your EC2 username (usually `ubuntu` or `ec2-user`)
   - **Private Key**: Enter directly or upload your SSH private key file
   - **Description**: "SSH key for EC2 app instance"

2. **EC2 Username** (Secret text):
   - **Kind**: Secret text
   - **ID**: Choose any ID (e.g., `ec2-username`)
   - **Secret**: Your EC2 username (e.g., `ubuntu`)
   - **Description**: "Username used by Jenkins in the test EC2 instance"

3. **EC2 Host** (Secret text):
   - **Kind**: Secret text
   - **ID**: Choose any ID (e.g., `ec2-host`)
   - **Secret**: Your EC2 instance private IP or hostname
   - **Description**: "Private IP of the test instance"

4. **Database URL** (Secret text):
   - **Kind**: Secret text
   - **ID**: Choose any ID (e.g., `database-url`)
   - **Secret**: Your RDS database connection string
     - Format: `postgresql+psycopg2://username:password@rds-proxy-endpoint:port/dbname`
     - Example: `postgresql+psycopg2://myuser:mypass@my-rds-proxy.region.rds.amazonaws.com:5432/mydb`
   - **Description**: "Link of the database (or proxy)"

5. **Flask Secret Key** (Secret text, Optional):
   - **Kind**: Secret text
   - **ID**: Choose any ID (e.g., `flask-secret-key`)
   - **Secret**: Your Flask secret key (generate a strong random key)
   - **Description**: "Secret key used with Flask"

### 2. Running the Pipeline

When you trigger the pipeline build, you will be prompted to provide the following parameters:

- **deployment_branch**: The Git branch to deploy (e.g., `main`, `develop`)
- **ec2_username**: Select the credential ID containing your EC2 username
- **ec2_host**: Select the credential ID containing your EC2 instance IP/hostname
- **database_url**: Select the credential ID containing your database connection string
- **flask_secret_key**: Select the credential ID containing your Flask secret key (optional)
- **flask_environment**: Type of environment (e.g., `production`, `staging`)
- **ssh_key**: Select the credential ID containing your SSH private key

**Note**: The pipeline uses these credential IDs to retrieve the actual values securely during execution. You don't need to hardcode any values in the Jenkinsfile.

### 3. Configure EC2 Instance

#### Initial Setup on EC2

SSH into your EC2 instance and run:

```bash
# Install Docker (if not already installed)
sudo apt-get update
sudo apt-get install -y docker.io docker-compose curl git

# Add your user to docker group (if needed)
sudo usermod -aG docker $USER

# Log out and back in for group changes to take effect
# Or run: newgrp docker

# Create deployment directory
mkdir -p /home/ubuntu/Personal-Finance-Manager
cd /home/ubuntu/Personal-Finance-Manager

# Clone the repository (if not already cloned)
# git clone <your-repo-url> .

# Verify Docker is working
docker --version
docker-compose --version
```

**Note**: 
- The deployment directory is `/home/ubuntu/Personal-Finance-Manager` (as configured in the Jenkinsfile)
- Environment variables are managed through Jenkins credentials and will be passed to Docker containers during deployment
- No `.env` file is needed on the EC2 instance
- The repository should already be cloned in the deployment directory before running the pipeline

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

### 4. Test the Pipeline

1. Go to your Jenkins job and click **Build with Parameters**
2. Fill in the required parameters:
   - **deployment_branch**: Enter the branch name (e.g., `main`, `develop`)
   - **ec2_username**: Select the credential ID containing your EC2 username
   - **ec2_host**: Select the credential ID containing your EC2 instance IP/hostname
   - **database_url**: Select the credential ID containing your database connection string
   - **flask_secret_key**: Select the credential ID containing your Flask secret key (optional)
   - **flask_environment**: Enter the environment type (e.g., `production`, `staging`)
   - **ssh_key**: Select the credential ID containing your SSH private key
3. Click **Build**
4. Monitor the Jenkins build console for any errors
5. Respond to the interactive prompts when they appear (or wait for the 5-minute timeout)
6. Verify deployment by accessing your app at `http://your-ec2-ip:5001`

**Note**: The pipeline can also be configured to trigger automatically via webhooks if desired, but it will still require parameter selection or default values.

## Pipeline Stages

The pipeline consists of the following stages:

1. **Check Connection**: 
   - Verifies SSH connectivity to the EC2 instance
   - Uses a 5-second timeout to test the connection
   - Prompts for user confirmation before proceeding (5-minute timeout)
   - If connection fails, the pipeline aborts immediately

2. **Deploy to EC2**: 
   - Retrieves all deployment credentials from Jenkins (database URL, secret key, environment variables)
   - Connects to EC2 instance via SSH
   - Navigates to the deployment directory (`/home/ubuntu/Personal-Finance-Manager`)
   - Sets environment variables (DATABASE_URL, FLASK_ENV, SECRET_KEY, FLASK_DEBUG=0, SEED_PREDEFINED=0)
   - Pulls latest changes from the specified Git branch
   - Stops previous Docker containers using `docker compose down`
   - Pulls latest Docker images
   - Builds and starts new containers with `docker compose up -d --build --remove-orphans`
   - Prints environment variables inside the Docker container for verification
   - Prompts for user confirmation after successful deployment (5-minute timeout)

**Note**: The pipeline includes interactive prompts between stages that require manual confirmation. Each prompt has a 5-minute timeout. If no response is received, the pipeline will proceed automatically after the timeout.

## Deployment Directory

The application is deployed to `/home/ubuntu/Personal-Finance-Manager` on the EC2 instance. The repository must already be cloned in this directory before running the pipeline.

## Troubleshooting

### Common Issues

#### SSH Connection Failed
- Verify SSH key credential is correctly configured in Jenkins and selected in the `ssh_key` parameter
- Check EC2 security group allows SSH from Jenkins IP
- Verify the `ec2_host` and `ec2_username` credential parameters are correctly set
- Test SSH connection manually: `ssh -i your-key.pem user@ec2-ip`
- Check the pipeline console output for the specific SSH error message

#### Docker Permission Denied
- Ensure user is in docker group: `sudo usermod -aG docker $USER`
- Log out and back in, or restart SSH session
- Verify Docker is running: `sudo systemctl status docker`

#### Pipeline Parameters Not Working
- Verify all required credentials are created in Jenkins (SSH key, EC2 username, EC2 host, database URL)
- Ensure credential IDs are correctly selected in pipeline parameters
- Check that credential types match: SSH key should be "SSH Username with private key", others should be "Secret text"
- Review Jenkins build console for credential-related errors

#### Environment Variables Not Loading
- Verify Jenkins credentials are correctly configured and selected in pipeline parameters:
  - `database_url` parameter should reference a credential ID containing the database connection string
  - `flask_secret_key` parameter should reference a credential ID containing the Flask secret key (optional)
  - `flask_environment` parameter should be set to the desired environment (e.g., `production`)
- Check Jenkins build console for credential errors
- Verify DATABASE_URL format matches: `postgresql+psycopg2://user:pass@host:port/dbname`
- Check the deployment logs - environment variables are printed inside the Docker container after deployment

#### Git Pull Fails
- Ensure the repository is already cloned in `/home/ubuntu/Personal-Finance-Manager`
- Verify the deployment branch specified in `deployment_branch` parameter exists
- Check Git remote is configured correctly on the EC2 instance
- Ensure the EC2 instance has network access to the Git repository

#### Docker Compose Issues
- Verify `docker-compose.prod.yml` file exists in the deployment directory
- Check Docker and Docker Compose are installed and working: `docker --version` and `docker-compose --version`
- Review container logs for application-specific errors

#### RDS Connection Issues
- Verify EC2 security group allows outbound to RDS proxy
- Check RDS proxy security group allows inbound from EC2
- Test connection manually: `psql -h rds-proxy-endpoint -U username -d dbname`
- Verify DATABASE_URL in Jenkins credentials uses the proxy endpoint, not direct RDS endpoint
- Check application logs for database connection errors

### Viewing Logs

On EC2 instance:
```bash
cd /home/ubuntu/Personal-Finance-Manager
docker compose -f docker-compose.prod.yml logs -f

# View only web container logs
docker compose -f docker-compose.prod.yml logs -f web

# View last 100 lines
docker compose -f docker-compose.prod.yml logs --tail=100
```

## Best Practices Implemented

✅ **Parameter-Based Configuration**: Credentials and deployment settings selected at build time via pipeline parameters  
✅ **SSH Connection Verification**: Tests SSH connectivity before attempting deployment  
✅ **Interactive Deployment Control**: User prompts between stages allow manual verification and control  
✅ **Secure Credentials**: All sensitive data (SSH keys, database URLs, secret keys) stored in Jenkins credentials (not in code)  
✅ **Environment Variable Injection**: Environment variables securely passed to Docker containers during deployment  
✅ **Resource Management**: Cleans up unused Docker images after pipeline execution  
✅ **Error Handling**: Proper error handling with clear failure messages and pipeline abort on connection failures  
✅ **Idempotent Deployments**: Can be run multiple times safely (stops old containers before starting new ones)  
✅ **Flexible Branch Deployment**: Supports deployment from any branch specified via parameter  
✅ **RDS Integration**: Uses RDS proxy for database connections (no local database container)  
✅ **Production Ready**: Separate production docker-compose configuration (`docker-compose.prod.yml`)  
✅ **Container Verification**: Prints environment variables inside Docker container for deployment verification  

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

Add notification steps in the pipeline post-actions:
```groovy
post {
    success {
        // slackSend(color: 'good', message: "Deployment successful: ${env.BUILD_URL}")
        // emailext(subject: "Deployment Successful", body: "Build ${env.BUILD_NUMBER} completed successfully")
    }
}
```

### Add Automated Testing Stage

Consider adding a test stage before deployment to ensure code quality:
```groovy
stage('Test') {
    steps {
        sh 'pytest tests/'
    }
}
```

### Add Health Check Stage

Implement a health check after deployment to verify the application is running:
```groovy
stage('Health Check') {
    steps {
        sh '''
            for i in {1..30}; do
                if curl -f http://${EC2_HOST}:5001/health; then
                    echo "Health check passed"
                    exit 0
                fi
                sleep 2
            done
            exit 1
        '''
    }
}
```

### Add Blue-Green Deployment

For zero-downtime deployments, consider implementing blue-green deployment strategy with multiple container instances.

### Add Database Migration Scripts

For production, consider using Alembic or similar migration tool instead of `db.create_all()` to manage database schema changes.

