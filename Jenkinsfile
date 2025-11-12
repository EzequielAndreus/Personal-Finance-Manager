pipeline {
    agent any
    
    options {
        timeout(time: 5, unit: 'MINUTES')
        timestamps()
    }
    
    parameters {
        string(
            defaultValue: 'main',
            description: 'Branch that will be pulled',
            name: 'deployment_branch'
        )
        credentials(
            defaultValue: 'pfm-production-username',
            credentialType: 'org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl',
            description: 'Username used by Jenkins in the test EC2 instance',
            name: 'ec2_username',
            required: true
        )
        credentials(
            defaultValue: 'pfm-production-host',
            credentialType: 'org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl',
            description: 'Private IP of the test instance',
            name: 'ec2_host',
            required: true
        )
        credentials(
            defaultValue: 'pfm-database-url',
            credentialType: 'org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl',
            description: 'Link of the database (or proxy)',
            name: 'database_url',
            required: true
        )
        credentials(
            defaultValue: 'pfm-flask-secret-key',
            credentialType: 'org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl',
            description: 'Secret key used with Flask',
            name: 'flask_secret_key',
            required: false
        )
        string(
            defaultValue: 'production',
            description: 'Type of environment in which the Flask app will be run',
            name: 'flask_environment'
        )
        credentials(
            defaultValue: 'pfm-production-ssh-key',
            credentialType: 'com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey',
            description: 'Private SSH key of the test instance',
            name: 'ssh_key',
            required: true
        )
    }
    
    environment {
        DEPLOYMENT_DIR = '/home/ubuntu/Personal-Finance-Manager'
        COMPOSE_FILE = 'docker-compose.prod.yml'
    }
    
    stages {
        stage('Check Connection') {
            steps {
                script {
                    def connectionVars = getConnectionCredentials()
                    sshagent([params.ssh_key]) {
                        checkSSHConnection(connectionVars)
                    }
                }
            }
        }
        stage('Deploy to EC2') {
            steps {
                script {
                    echo 'Deploying to EC2 instance...'
                    def envVars = getAllDeploymentCredentials()
                    sshagent([params.ssh_key]) {
                        deployToEC2(envVars)
                    }
                }
            }
            post {
                success {
                    echo 'Deployment successful!'
                    proceedMessage()
                }
                failure {
                    echo 'Deployment failed! Check logs above.'
                }
            }
        }
    }
    
    post {
        always {
            cleanDockerResources()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check logs for details.'
        }
        unstable {
            echo 'Pipeline is unstable.'
        }
    }
}

// Helper function to get connection credentials
def getConnectionCredentials() {
    def creds = [:]
    withCredentials([
        string(credentialsId: params.ec2_username, variable: 'EC2_USERNAME'),
        string(credentialsId: params.ec2_host, variable: 'EC2_HOST')
    ]) {
        creds = [
            EC2_USERNAME: env.EC2_USERNAME,
            EC2_HOST: env.EC2_HOST
        ]
    }
    return creds
}

// Helper function to get all deployment credentials
def getAllDeploymentCredentials() {
    def creds = [:]
    withCredentials([
        string(credentialsId: params.ec2_username, variable: 'EC2_USERNAME'),
        string(credentialsId: params.ec2_host, variable: 'EC2_HOST'),
        string(credentialsId: params.database_url, variable: 'DATABASE_URL'),
        string(credentialsId: params.flask_secret_key, variable: 'SECRET_KEY')
    ]) {
        creds = [
            EC2_USERNAME: env.EC2_USERNAME,
            EC2_HOST: env.EC2_HOST,
            DATABASE_URL: env.DATABASE_URL,
            SECRET_KEY: env.SECRET_KEY,
            FLASK_ENV: params.flask_environment,
            DEPLOYMENT_BRANCH: params.deployment_branch
        ]
    }
    return creds
}

// Helper function to check SSH connection
def checkSSHConnection(Map connectionVars) {
    echo "Checking SSH connectivity to ${connectionVars.EC2_USERNAME}@${connectionVars.EC2_HOST}..."
    
    def result = sh(
        script: """
            timeout 5s bash -c '
                ssh -o BatchMode=yes -o ConnectTimeout=5 \
                -o StrictHostKeyChecking=no ${connectionVars.EC2_USERNAME}@${connectionVars.EC2_HOST} "echo ok" \
                2>/dev/null
            '
        """,
        returnStatus: true
    )
    
    if (result != 0) {
        error "SSH connection to ${connectionVars.EC2_HOST} failed! Aborting pipeline."
    } else {
        echo "SSH connection to ${connectionVars.EC2_HOST} verified successfully."
        proceedMessage()
    }
}

// Helper function to deploy to EC2
def deployToEC2(Map envVars) {
    def remoteScript = """
        set -e
        
        echo "Navigating to deployment directory..."
        cd ${DEPLOYMENT_DIR}
        
        echo "Setting environment variables..."
        export DATABASE_URL="${envVars.DATABASE_URL}"
        export FLASK_ENV="${envVars.FLASK_ENV}"
        export SECRET_KEY="${envVars.SECRET_KEY}"
        export FLASK_DEBUG=0
        export SEED_PREDEFINED=0
        
        echo "Pulling latest changes..."
        git pull origin "${envVars.DEPLOYMENT_BRANCH}"
        
        echo "Stopping previous Docker container..."
        docker compose -f ${COMPOSE_FILE} down || true
        
        echo "Building and starting Docker containers..."
        docker compose -f ${COMPOSE_FILE} pull
        docker compose -f ${COMPOSE_FILE} up -d --build --remove-orphans
        
        echo "Printing environment variables inside Docker container..."
        docker compose -f ${COMPOSE_FILE} exec -T web env
        
        echo "Deployment completed successfully."
    """
    
    sh """
        ssh -o StrictHostKeyChecking=no "${envVars.EC2_USERNAME}@${envVars.EC2_HOST}" \
            DATABASE_URL="${envVars.DATABASE_URL}" \
            DEPLOYMENT_BRANCH="${envVars.DEPLOYMENT_BRANCH}" \
            SECRET_KEY="${envVars.SECRET_KEY}" \
            FLASK_ENV="${envVars.FLASK_ENV}" \
            bash -s << 'REMOTE_SCRIPT'
${remoteScript}
REMOTE_SCRIPT
    """
}

// Helper function to clean Docker resources
def cleanDockerResources() {
    sh '''
        # Clean up unused Docker images
        docker image prune -f || true
        
        # Only attempt docker-compose cleanup if docker-compose.yml exists
        # and we're in a directory that might have containers
        if [ -f docker-compose.yml ]; then
            # Check if there are any running containers from this compose file
            if docker-compose ps -q 2>/dev/null | grep -q .; then
                docker-compose down -v || true
            fi
        fi
    '''
}

def proceedMessage() {
    timeout(time: 10, unit: 'MINUTES') {
        input message: 'Proceed to the next stage?', ok: 'Proceed'
    }
}
