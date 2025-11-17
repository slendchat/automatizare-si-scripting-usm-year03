pipeline {
    agent { label 'ansible-agent' }

    stages {
        stage('Clone Ansible Repo') {
            steps {
                sh '''
                    rm -rf ansible
                    git clone https://github.com/slendchat/a-s_lab04_php_CICD-test.git ansible
                '''
            }
        }

        stage('Run Ansible Playbook') {
            steps {
                sh '''
                    cd ansible
                    ansible-playbook -i hosts.ini setup_test_server.yml
                '''
            }
        }
    }
}

