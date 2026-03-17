# AMPARO_BACKEND

## Um projeto de ajuda

## Pipeline CI/CD & Deploy na Nuvem

Para que o pipeline de CI/CD funcione corretamente, siga estes passos:

1.  **Conta AWS**: Crie uma conta na AWS.
2.  **Usuário IAM**: Crie um usuário IAM com privilégios necessários (ECS, ECR, S3, RDS, IAM, ou AdministratorAccess).
3.  **Configuração Local**: Configure suas credenciais localmente no seu terminal (usando `aws configure`).
4.  **GitHub Secrets**: No seu repositório GitHub, vá em *Settings > Secrets and variables > Actions* e adicione as chaves `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY` do usuário IAM criado.
5.  **Infraestrutura**: Navegue até a pasta de infraestrutura (`AMPARO_INFRA`) e execute os comandos do Terraform para provisionar os recursos:
    ```bash
    terraform init
    terraform plan
    terraform apply
    ```
6.  **Deploy**: Realize um `commit` e `push` para o repositório. Isso disparará automaticamente o workflow que construirá a imagem Docker, fará o push para o cloud (ECR) e atualizará os serviços (ECS).

