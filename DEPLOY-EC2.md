# Publicação do Aurora na AWS EC2

Este documento registra a configuração de publicação do Aurora na AWS usando
GitHub Actions, GitHub Container Registry (GHCR), Docker Compose e uma instância
EC2 com Amazon Linux 2023.

## Endereço publicado

- Aplicação: <http://ec2-3-137-205-13.us-east-2.compute.amazonaws.com>
- Região AWS: `us-east-2` (Ohio)
- Sistema da instância: Amazon Linux 2023, arquitetura `x86_64`
- Usuário SSH: `ec2-user`
- Diretório de implantação: `/opt/aurora`

O endereço acima usa HTTP na porta 80. HTTPS ainda não está configurado.

## Arquitetura do deploy

O workflow [`.github/workflows/deploy.yml`](./.github/workflows/deploy.yml)
executa testes do backend e build do frontend. Se ambos forem aprovados, cria e
publica duas imagens privadas no GHCR:

- `ghcr.io/jeffgitwebapp/aurora-backend`
- `ghcr.io/jeffgitwebapp/aurora-frontend`

Em pushes para `develop`, o workflow também se conecta à EC2 por SSH, copia
[`docker-compose.prod.yml`](./docker-compose.prod.yml), autentica a instância no
GHCR e atualiza os containers. As imagens implantadas recebem uma tag
correspondente ao SHA do commit. Tags de release no formato `v*` publicam
imagens, mas não executam o deploy na EC2.

Em produção, somente o frontend publica uma porta no host (`80`). O backend
fica disponível apenas na rede interna do Compose, e o Nginx do frontend
encaminha as chamadas `/api/` para ele.

## 1. Criar ou preparar a instância EC2

1. Na AWS, abra **EC2 → Instances** e crie uma instância com Amazon Linux 2023.
   A instância deste deploy é `x86_64`.
2. Selecione ou crie um par de chaves SSH e guarde o arquivo privado em local
   seguro. Ele será cadastrado como secret no GitHub; não o envie por mensagem
   nem o adicione ao repositório.
3. Use ou associe um Security Group com as regras necessárias:
   - **HTTP, TCP 80:** permita o tráfego dos visitantes que devem acessar a
     aplicação (por exemplo, `0.0.0.0/0`; inclua `::/0` se for servir IPv6).
   - **SSH, TCP 22:** limite a origem ao IP confiável necessário para
     administração ou ao runner usado no deploy. Runners hospedados pelo
     GitHub podem usar faixas de IP variáveis; não abra SSH para toda a
     internet apenas para contornar isso. Considere runner com IP de saída
     fixo ou AWS Systems Manager.
4. Confirme que a instância tem um endereço IPv4 público e DNS público. O DNS
   usado pela aplicação é:
   `ec2-3-137-205-13.us-east-2.compute.amazonaws.com`.
5. A conexão de administração usa o usuário `ec2-user`.

## 2. Instalar Docker Engine e Docker Compose v2 na EC2

Conecte-se à instância com SSH ou EC2 Instance Connect. No Amazon Linux 2023,
instale e inicie o Docker Engine:

```bash
sudo dnf install -y docker
sudo systemctl enable --now docker
sudo docker --version
```

O pacote `docker-compose-plugin` não estava disponível nos repositórios
configurados nessa instância. Por isso, instale o plugin Compose v2 manualmente
em um diretório global, para que também esteja disponível nos comandos `sudo`
do workflow:

```bash
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -fSL \
  https://github.com/docker/compose/releases/download/v5.6.0/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
sudo docker compose version
```

A instalação manual do Compose não é atualizada automaticamente. Para
atualizá-la, substitua a versão no endereço do download por uma versão desejada,
baixe o binário novamente para o mesmo caminho e confirme com
`sudo docker compose version`.

## 3. Validar a chave do host SSH

O workflow exige validação estrita da identidade SSH do servidor
(`StrictHostKeyChecking=yes`). O secret `EC2_KNOWN_HOSTS` deve conter a entrada
completa retornada por `ssh-keyscan` para o mesmo hostname cadastrado em
`EC2_HOST`, não apenas uma impressão digital `SHA256:...`.

1. Na EC2, obtenha a impressão digital da chave pública ED25519 do servidor:

   ```bash
   sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
   ```

2. Em um terminal confiável com OpenSSH, obtenha a entrada do hostname público:

   ```bash
   ssh-keyscan -T 10 -t ed25519 ec2-3-137-205-13.us-east-2.compute.amazonaws.com
   ```

3. Compare a impressão digital da chave obtida pelo `ssh-keyscan` com a
   impressão digital exibida na EC2. Só use a chave se forem iguais.
4. Cadastre a linha completa de `ssh-keyscan` em `EC2_KNOWN_HOSTS`. O primeiro
   campo precisa corresponder exatamente ao valor de `EC2_HOST`.

`ssh-keyscan` coleta a chave apresentada pelo host, mas não autentica o host
por si só. A comparação da impressão digital por um canal confiável é
necessária antes de confiar nessa entrada.

## 4. Criar token de leitura do GHCR

A EC2 precisa de credenciais para baixar as imagens privadas publicadas pelo
workflow.

1. No GitHub, acesse **Settings → Developer settings → Personal access tokens
   → Tokens (classic)**.
2. Gere um token classic com validade adequada e marque o escopo
   **`read:packages`**.
3. Se necessário, autorize o token para a organização proprietária dos pacotes
   e confirme que a conta tem acesso de leitura aos pacotes do Aurora.
4. Copie o token no momento da criação e guarde-o em um gerenciador seguro.
   Ele não deve ser colocado no código, no README, em logs ou em mensagens.

`read:packages` é a permissão que permite ao token baixar imagens do GitHub
Container Registry. Não é o nome de usuário. Para esta publicação, o usuário é
`jeffgitwebapp`.

## 5. Configurar os secrets do GitHub

No repositório, crie o environment **`production`** em
**Settings → Environments → New environment**. Dentro de
**Settings → Environments → production → Environment secrets**, cadastre:

| Secret | Valor |
| --- | --- |
| `EC2_HOST` | `ec2-3-137-205-13.us-east-2.compute.amazonaws.com` |
| `EC2_SSH_KEY` | Conteúdo da chave privada SSH autorizada para `ec2-user` |
| `EC2_KNOWN_HOSTS` | Linha completa do `ssh-keyscan`, após verificar a impressão digital |
| `GHCR_USERNAME` | `jeffgitwebapp` |
| `GHCR_READ_TOKEN` | Token classic com escopo `read:packages` |

Use **Environment secrets** do environment `production`, pois o job de deploy
declara `environment: production`. Nunca salve chave privada ou token em
`docker-compose.yml`, no workflow, em arquivos versionados ou na documentação.

## 6. Executar e acompanhar a publicação

O workflow é acionado por:

- push para a branch `develop`: executa verificações, publica as imagens e
  realiza deploy na EC2;
- push de uma tag `v*`: executa verificações e publica imagens, sem implantar
  automaticamente na EC2.

Para publicar uma alteração:

1. Faça commit e push para `develop`.
2. No GitHub, abra **Actions → Build and deploy Aurora**.
3. Confirme a aprovação dos jobs `backend-tests` e `frontend-build`.
4. Confirme a conclusão de `publish-images` e `deploy-ec2`.
5. Abra <http://ec2-3-137-205-13.us-east-2.compute.amazonaws.com> para validar a
   interface.

A publicação inicial foi concluída com sucesso na quarta tentativa da execução
[`aws` no GitHub Actions](https://github.com/jeffgitwebapp/aurora/actions/runs/40133253924).
As tentativas anteriores ajudaram a identificar e corrigir a configuração do
host SSH, a instalação do Docker/Compose na EC2 e as credenciais de leitura do
GHCR.

## 7. Verificar e administrar os containers

Conecte-se à EC2 e use estes comandos para verificar o estado:

```bash
cd /opt/aurora
sudo docker compose -f docker-compose.prod.yml ps
sudo docker compose -f docker-compose.prod.yml logs --tail=100
```

Para acompanhar logs em tempo real:

```bash
cd /opt/aurora
sudo docker compose -f docker-compose.prod.yml logs -f
```

Para conferir as imagens locais e o estado do serviço Docker:

```bash
sudo docker image ls
sudo systemctl status docker --no-pager
```

O arquivo `/opt/aurora/.env` é criado pelo workflow com o proprietário das
imagens e a tag do commit implantado. O arquivo Compose de produção define
reinício automático (`unless-stopped`) para os serviços.

## 8. Problemas encontrados e como identificar

- **`sudo: docker: command not found`**: Docker Engine não estava instalado na
  EC2. Instale o pacote `docker` e inicie o serviço com `systemctl`.
- **`No match for argument: docker-compose-plugin`**: o pacote não estava
  disponível nos repositórios configurados. Use a instalação manual do plugin
  Compose v2 descrita acima.
- **`Get "https://ghcr.io/v2/": denied`**: confira `GHCR_USERNAME`,
  `GHCR_READ_TOKEN`, validade do token, escopo `read:packages` e acesso da
  conta aos pacotes privados.
- **`Host key verification failed`**: confira se `EC2_KNOWN_HOSTS` contém a
  linha completa correspondente ao hostname em `EC2_HOST`, e se a impressão
  digital foi verificada.
- **Site indisponível apesar do deploy concluído**: confira se a regra TCP 80
  do Security Group permite o tráfego esperado, se os containers estão em
  execução e se o DNS público continua associado à instância.

## Segurança e limitações

- A aplicação está publicada em HTTP, sem TLS. Para uso com domínio ou dados
  reais, configure HTTPS e revise a arquitetura de segurança.
- A API atual é um protótipo e retorna uma resposta fixa; não é um serviço real
  de atendimento.
- O backend não publica sua porta diretamente na internet: ele é acessível
  pela rede interna do Compose através do proxy do frontend.
- Proteja a chave SSH e o token do GHCR, rotacione-os se forem expostos e
  mantenha o SSH limitado a origens confiáveis.
