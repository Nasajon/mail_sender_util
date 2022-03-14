@SET PYTHONPATH=%CD%
@SET PARAMS=-y --clean^
 --onefile^
 -p %PYTHONPATH%^
 --name "mail_cmd"^
 --icon icon.ico^
 --distpath "%NSBIN%"^
 --workpath "%NSDCU%"

@IF DEFINED JENKINS_HOME (
	@SET PARAMS=%PARAMS% --version-file "%WORKSPACE%\output\VersionInfo2"
)

@IF EXIST venv (
  @CALL @%CD%\venv\Scripts\deactivate.bat
)

@ECHO ##### Criando o ambiente virtual #####

@python -m venv --clear venv

@ECHO ##### Compilando o projeto #####

@CMD "/c @%CD%\venv\Scripts\activate.bat && @pip install -r requirements.txt && @pyinstaller %PARAMS% ./mail_sender_util/mail_cmd.py && @%CD%\venv\Scripts\deactivate.bat"
