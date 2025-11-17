pipeline {
    agent { label 'ssh-agent' }

    stages {
        stage('Clone PHP Project') {
            steps {
                sh '''
                    rm -rf project
                    git clone https://github.com/slendchat/a-s_lab04_php_CICD-test.git project
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    cd project
                    composer install --no-interaction --prefer-dist
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    cd project
                    vendor/bin/phpunit --log-junit junit.xml
                '''
            }
        }

        stage('Report Results') {
            steps {
                junit 'project/junit.xml'
            }
        }
    }
}

