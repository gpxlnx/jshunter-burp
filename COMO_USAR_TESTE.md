# Como Usar a Página de Teste

Para testar a extensão JSHunter localmente, você precisa servir os arquivos `test-page.html` e a pasta `scripts` usando um servidor web local.

## ⚡ Passo a Passo (Maneira Fácil)

### 1. Inicie um Servidor Web Local

Abra um terminal **na pasta do projeto** (`/home/gxavier/hacking/burpsuite/extensions/jshunter-burp`) e execute um dos comandos abaixo.

#### Opção A: Se você tem Python 3
```bash
python3 -m http.server 8000
```

#### Opção B: Se você tem Python 2
```bash
python -m SimpleHTTPServer 8000
```

#### Opção C: Se você tem Node.js/npm
```bash
# Instale o live-server globalmente (apenas uma vez)
npm install -g live-server

# Inicie o servidor
live-server .
```

Após executar o comando, você verá uma mensagem indicando que o servidor está rodando, algo como `Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/)`.

### 2. Configure o Burp Suite

1.  Abra o Burp Suite.
2.  Verifique se o proxy do Burp está ativo e configurado no seu navegador.
3.  Vá para a aba **JSHunter** e certifique-se de que a opção "Auto-scan JavaScript URLs" está marcada.

### 3. Acesse a Página de Teste

1.  Abra seu navegador (que está configurado para usar o proxy do Burp).
2.  Navegue para o seguinte endereço:
    ```
    http://localhost:8000/test-page.html
    ```
    ou
    ```
    http://127.0.0.1:8000/test-page.html
    ```

### 4. Verifique os Resultados

1.  **No Burp Suite:**
    *   Vá para a aba **Proxy** -> **HTTP history**. Você deve ver as requisições para `test-page.html`, `scripts/app.js`, e `scripts/vendor.js`.
    *   Vá para a aba **JSHunter**.
    *   Na tabela "Scan Results", você verá as URLs dos scripts escaneados.
    *   Na tabela "Findings Details", você verá os 4 secrets falsos que foram detectados.

2.  **No seu Discord/Telegram:**
    *   Se você configurou corretamente, deverá receber uma notificação com os secrets encontrados.

Isso confirma que a extensão está funcionando perfeitamente!
