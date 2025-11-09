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
        DEPLOY_DIR = '/home/ubuntu/Personal-Finance-Manager'
        // Docker Compose file for production
        COMPOSE_FILE = 'docker-compose.prod.yml'
        // Git repository URL
        REPO_URL = 'https://github.com/EzequielAndreus/Personal-Finance-Manager.git'
        // Branch to deploy
        DEPLOY_BRANCH = 'main'
        // EC2 connection details (configure in Jenkins credentials or pipeline parameters)
        EC2_USER = credentials('pfm-production-username')
        EC2_HOST = credentials('pfm-production-host')
        // Databse URL
        DATABASE_URL = credentials('pfm-database-url')
        SECRET_KEY = credentials('pfm-flask-secret-key')
        // Flask environment
        FLASK_ENV = 'production'
    }
    
    stages {
        stage('Check Connection') {
            steps {
                sshagent(['pfm-production-ssh-key']) {
                    script {
                        echo 'Checking SSH connectivity to ${EC2_USER}@${EC2_HOST} ...'
                        
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
        
        stage('Deploy to EC2') {
            steps {
                script {
                    echo 'Deploying to EC2 instance...'

                    // Connect using SSH
                    sshagent(['pfm-production-ssh-key']) {
                        sh """
                            ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} '
                                set -e
                                
                                echo "Navigating to deployment directory..."
                                cd ${DEPLOY_DIR}

                                echo "Setting environment variables..."
                                export DATABASE_URL="${DATABASE_URL}"
                                export SECRET_KEY="${SECRET_KEY}"
                                export FLASK_ENV='${FLASK_ENV}'
                                export FLASK_DEBUG=0
                                export SEED_PREDEFINED=0

                                echo "Pulling latest changes"
                                git pull origin main
                                
                                echo "Building and starting Docker containers..."
                                docker compose -f ${COMPOSE_FILE} pull
                                docker compose -f ${COMPOSE_FILE} up -d --build --remove-orphans
                                
                                echo "Deployment completed successfully."
                            '
                        """
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

