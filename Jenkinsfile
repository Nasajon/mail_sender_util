node('master') {
	def dirArtifactName = "mail_sender_util"
	def artifactUrl = "github.com/Nasajon/${dirArtifactName}.git"
	def artifactId = "mail_cmd"
	def artifactBuildPath = "${env.WORKSPACE}\\${dirArtifactName}\\"
	def nasajonCIBaseDir = "${env.NASAJON_CI_BASE_DIR}"

	try {
		properties([disableConcurrentBuilds()])

		stage('Checkout') {
			dir("${dirArtifactName}") {
			    timeout(time: 3600, unit: 'SECONDS') {
                	checkout scm
          		}
			}
		}

		stage('Build') {
			dir("${nasajonCIBaseDir}\\build\\erp") {
				bat 'init.bat'
			}

			generateVersionNumber()

			dir("${artifactBuildPath}") {
				bat 'jenkins_build.bat'
			}
		}
		
		stage('Tests') {
			//bat 'tests.bat'
		}
		

		stage('Deploy') {
			dir("${nasajonCIBaseDir}\\build\\erp") {
				bat "sign_file.bat ${env.WORKSPACE}\\output\\bin\\${artifactId}.exe"

				bat "deploy.bat ${artifactBuildPath} exe ${env.WORKSPACE}\\output\\bin\\${artifactId}.exe ${artifactId}"
			}

			withAWS(credentials: 'JENKINS_SP_UPLOAD', region: 'sa-east-1') {
				def bucket = env.BUCKET_CDN

				//Upload do artefato
				s3Upload(
					file: "${env.WORKSPACE}\\output\\bin\\${artifactId}.exe",
					bucket:"${bucket}",
					path:"${artifactId}/" + "${artifactId}_${currentBuild.displayName}.exe"
				)
			}


			//withAWS(credentials: 'JENKINS_AWS_CREDENTIALS') {
			//	def bucket = env.ERP_BUCKET

				//Upload do artefato
			//	s3Upload(
			//		file: "${env.WORKSPACE}\\output\\bin\\${artifactId}.exe",
			//		bucket:"${bucket}",
			//		path:"erp-update/artifacts/${artifactId}/${subFolders}/${artifactId}.exe",
			//		acl:'PublicRead')
			//}

		}

	} catch (e) {
		currentBuild.result = "FAILED"
    	notifyFailed()
    	throw e
	} finally {
		stage('Clean') {
			dir("${env.WORKSPACE}\\output") {
				deleteDir()
			}
		}
	}
}

def notifyFailed() {
  emailext(
		subject: '''${DEFAULT_SUBJECT}''',
		body: '''${DEFAULT_CONTENT}''',
		recipientProviders: [[$class: 'CulpritsRecipientProvider'],
							[$class: 'DevelopersRecipientProvider'],
							[$class: 'RequesterRecipientProvider'],
							[$class: 'UpstreamComitterRecipientProvider']],
		to: "${env.EMAILS_FAILED}"
	)
}

def generateVersionNumber() {
	def version = ""
	def branchName = "${env.BRANCH_NAME}"

	if (branchName == "master") {
		version = "2.${env.CURRENT_SPRINT}.0.${env.BUILD_NUMBER}"
	} else if (branchName == "v2.utf8") {
		version = "2.9998.${env.BUILD_NUMBER}.0"
	} else if (branchName.startsWith("v2.")) {
		def sprint = branchName.substring(3)
		version = "2.${sprint}.${env.BUILD_NUMBER}.0"
	} else {
		version = "2.0.0.0"
	}

	println("Version: " + version)

	currentBuild.displayName = version

	def file_version_template = readFile(
		file: "${env.WORKSPACE}\\mail_sender_util\\version_info.txt",
		encoding: "UTF-8"
	)

	file_version_template = file_version_template
		.replaceAll("__VERSION_INFO1__", version.replace(".", ", "))
		.replaceAll("__VERSION_INFO2__", version)

	writeFile file: "${env.WORKSPACE}\\output\\VersionInfo", text: version, encoding: "UTF-8"
	writeFile file: "${env.WORKSPACE}\\output\\VersionInfo2", text: file_version_template, encoding: "UTF-8"
}
