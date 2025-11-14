pipeline {
    agent any
    
    options {
        timeout(time: 10, unit: 'MINUTES')
        timestamps()
    }
    
    parameters {
        string(
            defaultValue: 'testing-env-01',
            name: 'environment_id',
            description: 'ID of the environment of this deployment'
        )
        string(
            defaultValue: 'PFM-95',
            name: 'issue_key',
            description: 'Issue key associated with this deployment'
        )
        string(
            defaultValue; 'Testing',
            name: 'environment_name',
            description: 'Name of the environment of this deployment'
        )
        choice (
            name: 'environment_type',
            description: 'Type of environment in which the deployment will be made',
            choices: ['testing', 'production']
        )
        string(
            defaultValue: 'main',
            description: 'Branch that will be pulled',
            name: 'deployment_branch'
        )
        credentials(
            defaultValue: 'pfm-test-username',
            credentialType: 'org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl',
            description: 'Username used by Jenkins in the test EC2 instance',
            name: 'ec2_username',
            required: true
        )
        credentials(
            defaultValue: 'pfm-test-host',
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
        TICKET_LINK = credentials('jira-ticket-browse')
    }
    
    stages {
        stage('Send notification') {
            steps {
                sendDeploymentInfoSlack('deployment in progress')
                sendDeploymentInfoJira('in_progress')
            }
        }
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
        stage('Testing') {
            steps {
                script {
                    echo 'Running tests...'
                    def envVars = getAllDeploymentCredentials()
                    sshagent([params.ssh_key]) {
                        runTests(envVars)
                    }
                }
            }
            post {
                success {
                    echo 'Test passed'
                    proceedMessage()
                }
                failure {
                    echo 'Test not passed'
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
            sendDeploymentInfoJira('successful')
            sendDeploymentInfoSlack('deployment successful')
        }
        failure {
            echo 'Pipeline failed. Check logs for details.'
            sendDeploymentInfoJira('failed')
            sendDeploymentInfoSlack('deployment failed')
        }
        unstable {
            echo 'Pipeline is unstable.'
            sendDeploymentInfoJira('unknown')
            sendDeploymentInfoSlack('deployment unstable')
        }
    }
}

// Helper function to send info to Slack
def sendDeploymentInfoSlack(String message) {
    slackSend(
        channel: "deployments-${params.environment_type}",
        message: "${TICKET_LINK}${params.issue_key} - ${message}"
    )
}

// Helper function to send info to Jira
def sendDeploymentInfoJira(String state) {
    jiraSendDeploymentInfo(
        environmentId: "${params.environment_id}",
        environmentName: "${params.environment_name}",
        environmentType: "${params.environment_type}",
        state: "${state}",
        issueKeys: ["${params.issue_key}"]
    )
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
        pwd
        
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

        echo "Checking if database migration is needed..."
        docker compose -f ${COMPOSE_FILE} exec web uv run python -c "from src.models import db; db.create_all()"
        
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

// Helper function to run tests
def runTests(Map envVars) {
    echo 'Running pytest on remote EC2...'
    def remoteScript = """
        set -e
        cd ${DEPLOYMENT_DIR}
        echo "Running pytest inside Docker service..."
        docker compose exec web uv run pytest
    """
    def status = sh(
        script: """
            ssh -o StrictHostKeyChecking=no "${envVars.EC2_USERNAME}@${envVars.EC2_HOST}" \
                bash -s << 'REMOTE_SCRIPT'
${remoteScript}
REMOTE_SCRIPT
        """,
        returnStatus: true
    )
    if (status != 0) {
        error "Tests failed (pytest exited with status ${status})."
    }
}

// Helper function to clean Docker resources
def cleanDockerResources() {
    sh '''
        # Clean up unused Docker images
        docker image prune -f || true
    '''
}

def proceedMessage() {
    try {
        timeout(time: 5, unit: 'MINUTES') {
            input message: 'Proceed to the next stage?', ok: 'Proceed'
        }
    } catch (org.jenkinsci.plugins.workflow.steps.FlowInterruptedException e) {
        echo "No response or manual abort detected: ${e}"
        // Specific actions when user does NOT proceed (timeout or abort)
        sendDeploymentInfoJira('cancelled')
        sendDeploymentInfoSlack('deployment cancelled - no manual approval')
        // Mark build accordingly and stop pipeline
        currentBuild.result = 'ABORTED'
        error('Pipeline aborted because manual approval was not provided.')
    } catch (Exception e) {
        echo "Unexpected error while waiting for input: ${e}"
        sendDeploymentInfoJira('failed')
        sendDeploymentInfoSlack('deployment failed while waiting for approval')
        currentBuild.result = 'FAILURE'
        error('Pipeline aborted due to input error.')
    }
}
