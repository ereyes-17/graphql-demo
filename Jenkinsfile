pipeline {
    agent any

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    environment {
        AWS_REGION      = 'us-east-1'
        CLUSTER_NAME    = 'my-cluster'
        IMAGE_REPO      = 'ereyes2017/graphql-demo'
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
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install -r requirements.txt
                    ruff check app --fix
                    python -m compileall app
                '''
            }
        }

        stage('Build & Push Docker Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKERHUB_USERNAME',
                    passwordVariable: 'DOCKERHUB_TOKEN'
                )]) {
                    script {
                        env.IMAGE_TAG  = "${env.BUILD_NUMBER}"
                    }
                    sh '''
                        echo "$DOCKERHUB_TOKEN" | docker login \
                            --username "$DOCKERHUB_USERNAME" \
                            --password-stdin

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
