pipeline {

    agent {
        label 'ec2-linux-spot-slave'
    }
    
    environment {
        IMAGE_NAME = 'bigdata/ceo-model'
        AWS_REGION = 'us-east-1'
        AWS_ACCOUNT = '820233355588'
        IMAGE_TAG = getShortCommitId()
        ENVIRONMENT = getEnvironment()
    }

    stages {
        stage('Initialize') {
            steps {
                notifyBuildDevOps()
                //notifyBuild()
            }
        }

        stage('Build image') {
            when {
                expression { isDevelop() || isRelease() || isMaster() }
            }
            steps {
                script {
                    def repositoryName = "${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com/${IMAGE_NAME}"
                    def concatImagesTags = ""

                    def defaultTagsList = [
                      "${repositoryName}:${IMAGE_TAG}",
                      "${repositoryName}:${getFixedImageTag()}"
                    ]

                    defaultTagsList.each { imageTag ->
                       concatImagesTags = "${concatImagesTags}" + " -t ${imageTag}"
                    }

                    sh "\$(aws ecr get-login --no-include-email --region ${AWS_REGION})"
                    sh "docker build ${concatImagesTags} ."
                }
            }
        }

        stage ('Push image') {
            when {
                expression { isDevelop() || isRelease() || isMaster() }
            }
            steps {
                script {
                    sh "\$(aws ecr get-login --no-include-email --region ${AWS_REGION})"
                    def repositoryName = "${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com/${IMAGE_NAME}"
                    sh "docker push ${repositoryName}"
                }
            }
        }
    }

    post {
        always {
            notifyBuildDevOps(currentBuild.result)
            //notifyBuild(currentBuild.result)
        }
        unstable {
            echo 'This will run only if the run was marked as unstable'
        }
    }
}

def getEnvironment(){
  return (isDevelop())?'dev':(isRelease()?'qas':(isMaster())?'prd':'dev')
}

def getFixedImageTag(){
  return (isDevelop())?'dev':(isRelease()?'qas':(isMaster())?'latest':'dev')
}

def isMaster() {
    return env.BRANCH_NAME == "master"
}

def isRelease() {
    return env.BRANCH_NAME ==~ '^release\\/[\\w\\d\\.]*$'
}

def isDevelop() {
    return env.BRANCH_NAME == "develop"
}

def getReleaseVersion() {
    def branchName = env.BRANCH_NAME
    return branchName.substring(branchName.indexOf('/') + 1)
}

def getShortCommitId() {
    def gitCommit = env.GIT_COMMIT
    def shortGitCommit = "${gitCommit[0..6]}"
    return shortGitCommit
}

def notifyBuild(String buildStatus = 'STARTED') {
    // default build status in case is not passed as parameter
    buildStatus = buildStatus ?: 'SUCCESS'

    // variables and constants
    def colorName = 'RED'
    def colorCode = '#FF0000'
    def from = 'jenkins@belcorp.biz'
    def subject = "${buildStatus}: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'"
    def url = "https://devops.belcorp.biz/job/${env.BUILD_ID}?name=${env.JOB_NAME}"
    def summary = "${subject} (${url})"
    def details = "<p>${buildStatus}: Job <a href='${url}}]</a></p>"

    // override default values based on build status
    if (buildStatus == 'STARTED') {
        color = 'YELLOW'
        colorCode = '#FFFF00'
    } else if (buildStatus == 'SUCCESS') {
        color = 'GREEN'
        colorCode = '#00FF00'
    } else {
        color = 'RED'
        colorCode = '#FF0000'
    }

    slackSend (
        color: colorCode,
        message: summary,
        channel: '#jenkins',
        teamDomain: 'oapi-belcorp',
        tokenCredentialId: 'slack_oapi_token')

}

def notifyBuildDevOps(String buildStatus = 'STARTED') {
    buildStatus = buildStatus ?: 'SUCCESS'
    String buildPhase = (buildStatus == 'STARTED') ? 'STARTED' : 'FINALIZED'
    commit = (buildStatus == 'STARTED') ? 'null' : sh(returnStdout: true, script: "git log -n 1 --pretty=format:'%h'")

    sh """curl -H "Content-Type: application/json" -X POST -d '{
        "name": "${env.JOB_NAME}",
        "type": "pipeline",
        "build": {
            "phase": "${buildPhase}",
            "status": "${buildStatus}",
            "number": ${env.BUILD_ID},
            "scm": {
                "commit": "${commit}"
            },
            "artifacts": {}
        }
    }' https://devops.belcorp.biz/gestionar_despliegues_qa"""
}
