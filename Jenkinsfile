pipeline {
    agent {
        label 'ec2'
    }

    environment {  
        SONARQUBE_SERVER = "http://34.229.189.199:9000/"
        AWS_ECR_REGION = "us-east-1"
        AWS_ECR_REPOSITORY = "jenkins-poc"
        DOCKER_IMAGE_NAME = "hello-world-app"
        SONARQUBE_LOGIN_TOKEN = "sqa_9eeff9fd6fe6cc1ba506f3053f98af90e1236886"
        AWS_ECR_ACCOUNT_ID = "905418319927"
        AWS_ACCESS_KEY_ID = "AKIA5FTZDFA3WXWEKNEN"
        AWS_SECRET_ACCESS_KEY = "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"
        PUBLIC_IP = "34.229.189.199"
    }

    stages {
        stage('Checkout') {
            steps {
                retry(3) {
                    checkout([$class: 'GitSCM', branches: [[name: '*/main']], userRemoteConfigs: [[url: 'https://github.com/shekharbo/hello-world.git']]])
                }
            }
        }

        stage('Unit Test') {
            steps {
                sh 'docker --version'
                sh 'docker pull python:3.9'
                sh 'pip install -r requirements.txt'
                sh 'python3 -m venv ~/myenv'
                sh """
                set +x
                . /home/ubuntu/myenv/bin/activate
                """
                sh """
                /home/ubuntu/.local/bin/pytest /home/ubuntu/workspace/hello_world_demo/tests/test_main.py
               """
            }
        }

        stage('Code Coverage') {
            steps {
                sh 'pip install coverage'
                sh """
                /home/ubuntu/.local/bin/coverage run -m pytest /home/ubuntu/workspace/hello_world_demo/tests/test_main.py
                """
                sh '/home/ubuntu/.local/bin/coverage report'
                sh '/home/ubuntu/.local/bin/coverage xml -o coverage.xml'
                cobertura coberturaReportFile: 'coverage.xml'
            }
        }

        stage('SCA and SonarQube') {
            steps {
                withSonarQubeEnv('SonarQubeServer') {
                    script {
                        def scannerHome = tool 'SonarQubeScanner'
                        if (scannerHome) {
                            sh "/home/hello-world-demo-python/hello-world/sonar-scanner-5.0.1.3006-linux/bin/sonar-scanner \
                                -Dsonar.projectKey=hello-world \
                                -Dsonar.sources=src \
                                -Dsonar.host.url=${SONARQUBE_SERVER} \
                                -Dsonar.login=${SONARQUBE_LOGIN_TOKEN}"
                        } else {
                            error "SonarQube Scanner not configured."
                        }
                    }
                }
            }
        }

        stage('Build and tag image using Docker') {
            steps {
                script {
                    dir('/home/ec2-user/hello-world/hello_world') {
                        sh 'pwd'
                        sh 'ls -l Dockerfile'
                        sh 'docker build -t hello-world-app .'
                        sh "docker tag hello-world-app ${AWS_ECR_ACCOUNT_ID}.dkr.ecr.${AWS_ECR_REGION}.amazonaws.com/${AWS_ECR_REPOSITORY}:latest"
                        withCredentials([usernamePassword(credentialsId: 'aws-ecr-credentials', usernameVariable: 'AWS_ACCESS_KEY_ID', passwordVariable: 'AWS_SECRET_ACCESS_KEY')]) {
                            sh "aws ecr get-login-password --region ${AWS_ECR_REGION} | docker login --username AWS --password-stdin ${AWS_ECR_ACCOUNT_ID}.dkr.ecr.${AWS_ECR_REGION}.amazonaws.com"
                            sh "docker push ${AWS_ECR_ACCOUNT_ID}.dkr.ecr.${AWS_ECR_REGION}.amazonaws.com/${AWS_ECR_REPOSITORY}:latest"
                        }
                    }
                }
            }
        }

        stage('Image scan using trivy') {
            steps {
                sh "trivy image ${AWS_ECR_ACCOUNT_ID}.dkr.ecr.${AWS_ECR_REGION}.amazonaws.com/${AWS_ECR_REPOSITORY}:latest"
            }
        }

        stage('Deploy to EC2') {
            steps {
                sshagent(['ssh_key']) {
                    sh "ssh -o StrictHostKeyChecking=no ubuntu@$PUBLIC_IP aws ecr get-login-password --region ${AWS_ECR_REGION} | docker login --username AWS --password-stdin ${DOCKER_REGISTRY}"
                    sh "ssh -o StrictHostKeyChecking=no ubuntu@$PUBLIC_IP docker pull ${AWS_ECR_ACCOUNT_ID}.dkr.ecr.${AWS_ECR_REGION}.amazonaws.com/${AWS_ECR_REPOSITORY}:latest"
                    sh "ssh -o StrictHostKeyChecking=no ubuntu@$PUBLIC_IP docker run -d -p 8081:8080 ${AWS_ECR_ACCOUNT_ID}.dkr.ecr.${AWS_ECR_REGION}.amazonaws.com/${AWS_ECR_REPOSITORY}:latest"
                }
            }
        }
    }
}
