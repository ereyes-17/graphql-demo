pipeline {
    agent any

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    environment {
        AWS_REGION      = 'us-east-1'
        CLUSTER_NAME    = 'my-cluster'
        IMAGE_NAME      = 'graphql-demo'
        HELM_CHART_API  = './k8s/helm/api'
        HELM_CHART_DB   = './k8s/helm/postgres'
        NAMESPACE       = 'graphql-demo'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Download and Install AWS CLI') {
            steps {
                sh '''
                    sudo rm -rf aws/dist
                    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
                    unzip awscliv2.zip
                    ./aws/install
                    aws --version
                '''
            }
        }

        stage('Configure AWS & Kubeconfig') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding',
                                  credentialsId: 'aws-credentials',
                                  accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                                  secretKeyVariable: 'AWS_SECRET_ACCESS_KEY']]) {
                    sh '''
                        aws --version
                        aws sts get-caller-identity
                        aws eks update-kubeconfig \
                            --region ${AWS_REGION} \
                            --name ${CLUSTER_NAME}
                        kubectl config current-context
                    '''
                }
            }
        }

        stage('Lint / Test') {
            steps {
                sh '''
                    python -m venv .venv
                    . .venv/bin/activate
                    pip install -r requirements.txt
                    ruff check app
                    python -m compileall app
                '''
            }
        }

        stage('Build & Push Docker Image') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding',
                                  credentialsId: 'aws-credentials',
                                  accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                                  secretKeyVariable: 'AWS_SECRET_ACCESS_KEY']]) {
                    script {
                        env.AWS_ACCOUNT_ID = sh(
                            script: 'aws sts get-caller-identity --query Account --output text',
                            returnStdout: true
                        ).trim()
                        env.IMAGE_REPO = "${env.AWS_ACCOUNT_ID}.dkr.ecr.${env.AWS_REGION}.amazonaws.com/${env.IMAGE_NAME}"
                        env.IMAGE_TAG  = "${env.BUILD_NUMBER}"
                    }
                    sh '''
                        aws ecr get-login-password --region ${AWS_REGION} | \
                            docker login --username AWS --password-stdin ${IMAGE_REPO%/*}

                        docker build -t ${IMAGE_REPO}:${IMAGE_TAG} -t ${IMAGE_REPO}:latest .

                        docker push ${IMAGE_REPO}:${IMAGE_TAG}
                        docker push ${IMAGE_REPO}:latest
                    '''
                }
            }
        }

        stage('Deploy to EKS') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding',
                                  credentialsId: 'aws-credentials',
                                  accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                                  secretKeyVariable: 'AWS_SECRET_ACCESS_KEY']]) {
                    sh '''
                        aws eks update-kubeconfig \
                            --region ${AWS_REGION} \
                            --name ${CLUSTER_NAME}

                        helm upgrade --install postgres ${HELM_CHART_DB} \
                            -n ${NAMESPACE} \
                            --create-namespace \
                            --wait

                        helm upgrade --install graphql-demo-api ${HELM_CHART_API} \
                            -n ${NAMESPACE} \
                            --set workload.image=${IMAGE_REPO}:${IMAGE_TAG} \
                            --wait

                        kubectl rollout status deployment/graphql-demo-api -n ${NAMESPACE}
                    '''
                }
            }
        }
    }

    post {
        always {
            sh 'rm -rf .venv'
        }
        failure {
            echo 'Build or deployment failed.'
        }
        success {
            echo "Deployed ${IMAGE_REPO}:${IMAGE_TAG} to EKS cluster ${CLUSTER_NAME}."
        }
    }
}
