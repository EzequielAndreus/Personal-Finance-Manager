pipeline {
    agent any
    
    options {
        // Discard old builds to save disk space
        buildDiscarder(logRotator(numToKeepStr: '10'))
        // Timeout after 10 minutes
        timeout(time: 10, unit: 'MINUTES')
        // Add timestamps to console output
        timestamps()
        // Retry on failure (optional)
        retry(2)
    }
    
    environment {
        // Application name
        APP_NAME = 'personal-finance-manager'
        // Deployment directory on EC2
        DEPLOY_DIR = '/opt/pfm'
        // Docker Compose file for production
        COMPOSE_FILE = 'docker-compose.prod.yml'
        // Branch to deploy
        DEPLOY_BRANCH = 'main'
        // EC2 connection details (configure in Jenkins credentials or pipeline parameters)
        EC2_USER = credentials('pfm-production-username')
        EC2_HOST = credentials('pfm-production-host')
    }
    
    stages {
        stage('Check Connection') {
            steps {
                sshagent(['pfm-production-ssh-key']) {
                    script {
                        echo '🔍 Checking SSH connectivity to ${EC2_USER}@${EC2_HOST} ...'
                        
                        // Run a short SSH test with a 5-second timeout
                        def result = sh(
                            script: '''
                                timeout 5s bash -c '
                                    ssh -o BatchMode=yes -o ConnectTimeout=5 \
                                    -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} 'echo ok' \
                                    2>/dev/null
                                '
                            ''',
                            returnStatus: true
                        )

                        if (result != 0) {
                            error 'SSH connection to ${EC2_HOST} failed! Aborting pipeline.'
                        } else {
                            echo 'SSH connection to ${EC2_HOST} verified successfully.'
                        }
                    }
                }
            }
        }

        stage('Checkout') {
            steps {
                script {
                    echo 'Checking out code from ${env.GIT_BRANCH}'
                    checkout scm
                    
                    // Verify we're on the main branch
                    /*
                    def branch = env.GIT_BRANCH ?: sh(
                        script: 'git rev-parse --abbrev-ref HEAD',
                        returnStdout: true
                    ).trim()
                    
                    if (!branch.contains('main')) {
                        error('This pipeline only deploys from main branch. Current branch: ${branch}')
                    }
                    */
                }
            }
        }
        
        /*
        stage('Test') {
            steps {
                script {
                    echo 'Running test suite...'
                    withCredentials([
                        string(credentialsId: 'pfm-database-url', variable: 'DATABASE_URL'),
                        string(credentialsId: 'pfm-flask-secret-key', variable: 'SECRET_KEY')
                    ]) {
                    sh '''
                        # Create a temporary .env file for docker-compose
                        echo "DATABASE_URL=${DATABASE_URL}" > .env
                        echo "SECRET_KEY=${SECRET_KEY}" >> .env

                        # Build test image
                        docker-compose build web
                        
                        # Check connection to the database
                        echo 'Checking database connection...'
                        docker-compose run --rm web python -c "
import psycopg2
import os
import sys

try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'].replace('postgresql+psycopg2://', 'postgresql://'))
    print('Connection successful!')
    conn.close()
except Exception as e:
    print('Connection failed:', e)
    sys.exit(1)
"

                        # Run tests
                        docker-compose run --rm web python -m pytest -v || exit 1

                        # Clean up .env file
                        rm -f .env
                    '''
                    }
                }
            }
            post {
                always {
                    // Clean up test containers
                    sh 'docker-compose down -v || true'
                }
            }
        }
        */
        
        /*
        stage('Build') {
            steps {
                script {
                    echo 'Building Docker image...'
                    sh '''
                        # Build production image
                        docker build -t ${APP_NAME}:${BUILD_NUMBER} .
                        docker tag ${APP_NAME}:${BUILD_NUMBER} ${APP_NAME}:latest
                    '''
                }
            }
        }
        */
        
        stage('Deploy to EC2') {
            steps {
                script {
                    echo 'Deploying to EC2 instance...'

                    // Check that DEPLOY_DIR is set
                    if (!DEPLOY_DIR) {
                        error 'DEPLOY_DIR is not set! Aborting deployment.'
                    }
                    echo "Deployment directory: ${DEPLOY_DIR}"
                    
                    // Use SSH to deploy to EC2 with environment variables from Jenkins credentials
                    sshagent(credentials: ['pfm-production-ssh-key']) {
                        // Create deployment directory and backup folder
                        sh '''
                            ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${EC2_USER}@${EC2_HOST} \\
                            sudo mkdir -p $DEPLOY_DIR \\
                            sudo mkdir -p $DEPLOY_DIR/backup \\
                        '''
                        
                        script {
                            // Use the workspace repo URL and desired branch to update on the server instead of copying files
                            def REPO_URL = sh(script: "git config --get remote.origin.url", returnStdout: true).trim()
                            def BRANCH = env.DEPLOY_BRANCH ?: sh(script: 'git rev-parse --abbrev-ref HEAD', returnStdout: true).trim()

                            sh """
                                ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${EC2_USER}@${EC2_HOST} bash -s << 'REMOTE_SCRIPT'
                                    set -e

                                    mkdir -p ${DEPLOY_DIR}
                                    cd ${DEPLOY_DIR}

                                    if [ -d ".git" ]; then
                                        echo "Repository exists on remote — updating..."
                                        git fetch --all --prune
                                        # Ensure branch exists and reset to remote branch
                                        git checkout ${BRANCH} || git checkout -b ${BRANCH} origin/${BRANCH} || true
                                        git reset --hard origin/${BRANCH} || true
                                    else
                                        echo "Cloning repository on remote..."
                                        git clone --depth 1 --branch ${BRANCH} '${REPO_URL}' ${DEPLOY_DIR}
                                        cd ${DEPLOY_DIR}
                                    fi

                                    # Bring services up (pull images if updated, then rebuild/start)
                                    docker-compose -f ${COMPOSE_FILE} pull || true
                                    docker-compose -f ${COMPOSE_FILE} up -d --build
                        REMOTE_SCRIPT
                            """
                        }


                        // Create backup of current deployment
                        /*
                        sh '''
                            ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${EC2_USER}@${EC2_HOST} \\
                                'if [ -d ${DEPLOY_DIR}/.git ]; then \\
                                    cd ${DEPLOY_DIR} && \\
                                    tar -czf ${DEPLOY_DIR}/backup/backup-\\
                                    $(date +%Y%m%d-%H%M%S).tar.gz . || true; \\
                                 fi'
                        '''
                        */
                        
                        // Copy files to EC2 (excluding unnecessary files)
                        /*
                        sh '''
                            rsync -avz --delete \\
                                --exclude '.git' \\
                                --exclude '__pycache__' \\
                                --exclude '*.pyc' \\
                                --exclude '.env' \\
                                --exclude 'instance/' \\
                                --exclude 'dist/' \\
                                --exclude 'tests/' \\
                                --exclude '.pytest_cache' \\
                                --exclude 'uv.lock' \\
                                -e 'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null' \\
                                ./ ${EC2_USER}@${EC2_HOST}:${DEPLOY_DIR}/
                        '''
                        */
                        
                        /*
                        // Deploy on EC2 with environment variables from Jenkins credentials
                        withCredentials([
                            string(credentialsId: 'pfm-database-url', variable: 'DATABASE_URL'),
                            string(credentialsId: 'pfm-flask-secret-key', variable: 'SECRET_KEY'),
                            string(credentialsId: 'pfm-flask-env', variable: 'FLASK_ENV', defaultValue: 'production'),
                            string(credentialsId: 'pfm-seed-predefined', variable: 'SEED_PREDEFINED', defaultValue: '0')
                        ]) {
                            // Deploy on EC2 - pass environment variables via SSH command
                            // Use unquoted heredoc so Jenkins variables expand, but escape remote shell variables
                            sh '''
                                ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${EC2_USER}@${EC2_HOST} bash -s << REMOTE_SCRIPT
                                    set -e
                                    cd ${DEPLOY_DIR}
                                    
                                    # Export environment variables from Jenkins credentials
                                    export DATABASE_URL='${DATABASE_URL}'
                                    export SECRET_KEY='${SECRET_KEY}'
                                    export FLASK_ENV='${FLASK_ENV}'
                                    export FLASK_DEBUG=0
                                    export SEED_PREDEFINED='${SEED_PREDEFINED}'
                                    export PORT=5000
                                    
                                    # Stop existing containers gracefully
                                    docker-compose -f ${COMPOSE_FILE} down || true
                                    
                                    # Remove old unused images (keep last 2)
                                    docker image prune -f || true
                                    
                                    # Build new containers
                                    echo 'Building Docker images...'
                                    docker-compose -f ${COMPOSE_FILE} build --no-cache
                                    
                                    # Start new containers with environment variables
                                    echo 'Starting containers...'
                                    docker-compose -f ${COMPOSE_FILE} up -d
                                    
                                    # Wait for services to be healthy
                                    echo 'Waiting for services to be healthy...'
                                    sleep 15
                                    
                                    # Run database migrations if needed
                                    echo 'Running database migrations...'
                                    docker-compose -f ${COMPOSE_FILE} exec -T web python -c \\
                                        'from src.app import create_app; from src.models import db; \\
                                         app = create_app(); app.app_context().push(); db.create_all()' || true
                                    
                                    # Health check
                                    echo 'Performing health check...'
                                    MAX_RETRIES=30
                                    RETRY_COUNT=0
                                    while [ \\\\$RETRY_COUNT -lt \\\\$MAX_RETRIES ]; do
                                        if curl -f http://localhost:5001/ > /dev/null 2>&1; then
                                            echo 'Health check passed!'
                                            exit 0
                                        fi
                                        RETRY_COUNT=\\\\$((RETRY_COUNT + 1))
                                        echo 'Waiting for application to be ready... (\\\\$RETRY_COUNT/\\\\$MAX_RETRIES)'
                                        sleep 2
                                    done
                                    
                                    echo 'Health check failed after \\\\$MAX_RETRIES attempts'
                                    docker-compose -f ${COMPOSE_FILE} logs --tail=50
                                    exit 1
REMOTE_SCRIPT
                            '''
                            */
                        }
                    }
                }
            }
            post {
                success {
                    script {
                        echo 'Deployment successful!'
                        // Optional: Send notification
                        // slackSend(color: 'good', message: 'Deployment successful: ${env.BUILD_URL}')
                    }
                }
                failure {
                    script {
                        echo 'Deployment failed! Check logs above.'
                        // Optional: Rollback logic
                        // sshagent(credentials: ['pfm-production-ssh-key']) {
                        //     sh 'ssh ${EC2_USER}@${EC2_HOST} 'cd ${DEPLOY_DIR} && docker-compose -f ${COMPOSE_FILE} down && [ -d backup ] && tar -xzf \$(ls -t backup/*.tar.gz | head -1) -C .''
                        // }
                    }
                }
            }
        }
    }
    
    post {
        always {
            // Clean up local Docker images
            sh '''
                docker image prune -f || true
                docker-compose down -v || true
            '''
            
            // Archive artifacts (optional)
            archiveArtifacts artifacts: '**/*.log', allowEmptyArchive: true
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

