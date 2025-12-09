# Streamlit Cloud Deployment Guide

## Quick Deploy Steps

### 1. Push to GitHub (Already Done)
Repository: `https://github.com/adimStrong/Juan365DanceCrazeAll-in-One-Sa-SAya`

### 2. Connect to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select repository: `adimStrong/Juan365DanceCrazeAll-in-One-Sa-SAya`
5. Branch: `main`
6. Main file path: `streamlit_app.py`

### 3. Add Secrets (IMPORTANT!)
In Streamlit Cloud dashboard:
1. Click your app's "..." menu → "Settings"
2. Go to "Secrets" section
3. Paste the following TOML configuration:

```toml
[gcp_service_account]
type = "service_account"
project_id = "juan365-reporter"
private_key_id = "9150e60c695d61263b9dba6657ce8aa82a0550c3"
private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCoGThkPpBaBfUT\n56HqZQhUPuD3mb8hRxS4jC3E3m/HT+0yT5rwzqovglUChhnETZzsvR8QGlQO/eDD\npD9cCNxWWCnD/v/y6v+ihS6ujlmaS7xxc2bU5+EqkgCaBxUv9ALuhBBoFEZRxl63\nqWqNYusqaqbjYEFHmnXO5gCR6LHrWIyV0q5VutyombTwAxen6LzsWAf36N+nt+dW\nGA0dgd6uhxFH8jxLtU0qcd3ZGNgK3Ru41ORwOvBBdvDHdKXkP2Rq18YiSsx2graw\nAxunBRxHcEeBggIh6OprTol6IkraZEg1XI4YMNllcT2S5GY3xLaYxw7y5s+7OF5G\n9Be3FparAgMBAAECggEADRAwrrGh/Cz8V7inf5Ssagec6gD7tnVUqebS47q5iw6u\nCzveeZpF5X1GZ/TN6dByQn+L+29gWu3l2q5X8ioKHXeqfz3A3Drg9NtOvmf3lKMQ\nGOzz79W5TNqdy1qDjf9zft+qerwgnthAohs7WZN3XQt+vqrLR+o7/4EmSDCCKxzN\nMAEtaI6WfUIu2UBJckkVI0HWcPnhrEEMDumqytFovzJ/ImMDMcjeof0dr0lmnFQG\nWh2GgKIhYxhP3BERPPbD68/+lfEHLFI3ZfLMKlYImkOFd9VethIr469suhyZ/ier\nretAwZeEuzJawes3PQK8oH2f+W20ZM+iEmjpgTfG6QKBgQDgl9d5qRh3zpnZjWXR\nXiA1pDbgLoTN+NnY8GcnQJsF0ZQNvsP3oCZn/LUGO5qHfU63oPRkIQtKpRbEFXNq\nWsmExV9NqZx77MfqtXG/N9G88fhinmUgYLynuAYHuHzfCr1lq+TuBU4Hq9kO77aa\nCzoNBt03e+vSxzyOLJLndEnn9wKBgQC/mvDUlLVXcEIZ18aB0tRepodPJ1Hw50dl\naHgp2N7TmuOD+A7fpcZEL8+oZWSvRBZGBxg20FXlybra5SDIoSKXFbd7pC37a/QD\nNjj9RqBzX+rQQrmhmBy7Csdnyu2/UEwQcxpMpD0hG5tmxQ8T5A+H+0GhoNEtLn2n\nSSCAbVwh7QKBgHFe9JwrKXjAx5Sz9aOcOfIZ9MFxegRnC8CgidGcoSRsyKmvlEiZ\nhQmU3ORKjhS6wlObYgJxU7vYXgeZNGuJbJQi9ZrEdYNw4PGvqb12td8E3fcaMb4I\nVvLqx9B55j7IsxZxkNw9vUfODYGmq6xS4njU8DIj0cTSYdT61yUS5IO9AoGAcj5M\nAjR4u53vi8EgVyACCD16yDNFpEICS/CyVSE+GyVrKrCpDaimQtnPEzUBh48tSKvK\nQESQMubJRuL/XSDWowcL0+jckeCYKaIW8M0/tgsm0u42CKfN2ahfpP9WKpASCmzW\n7YOv/yGa0vgEOXPt3sJtK5XbovjpaukrO+f42zECgYAfQpQzvSrxdeGCKidWvHb/\nnoJxHmJgKG8GgxT5KjQO0n85dS/6C5XgKe0DH+siu/hzDn0XlzzJQr84jyGDi3xa\nmw6qWG7UfmPoLI8kV1zZPZj/nCNzQ1TMJvg2mEdtvi7u7DCvBHdh9cc2ml7mZ415\nBVkEqqt3vcHR4fiQuGL2kQ==\n-----END PRIVATE KEY-----\n"
client_email = "juan365videoscrapper@juan365-reporter.iam.gserviceaccount.com"
client_id = "115957953125050857604"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/juan365videoscrapper%40juan365-reporter.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
```

4. Click "Save"

### 4. Deploy
The app will automatically deploy after saving secrets.

## Local Development
For local development, just place `credentials.json` in the project folder.
The app automatically detects whether to use Streamlit secrets or local file.

## Data Source
- Google Sheet ID: `1GB-FfBOykCuXUwbz6Mpp7-JyWSMgK-5jtoPc3xV86_w`
- Service Account: `juan365videoscrapper@juan365-reporter.iam.gserviceaccount.com`

Make sure the Google Sheet is shared with the service account email!
