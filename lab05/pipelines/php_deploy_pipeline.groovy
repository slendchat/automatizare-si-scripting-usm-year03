pipeline {
    agent { label 'ansible-agent' }

    stages {
        stage('Clone PHP Project') {
            steps {
                sh '''
                    rm -rf project
                    git clone https://github.com/slendchat/a-s_lab04_php_CICD-test.git project
                '''
            }
        }

        stage('Deploy to Test Server') {
            steps {
                sh '''
                    ansible-playbook \
                      -i ansible/hosts.ini \
                      ansible/deploy_php_project.yml
                '''
            }
        }
    }
}

