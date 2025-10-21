# Guia de Migração - Discord para Telegram

## Versão 2.0.0

Este guia ajudará você a migrar da versão 1.0.0 (Discord) para a versão 2.0.0 (Telegram).

## 🚨 Mudanças Importantes

A versão 2.0.0 substitui completamente a integração com Discord por Telegram. Não há mais suporte para webhooks do Discord.

## 📝 O que foi Alterado

### Arquivos Modificados

1. **jshunter_extension.py** (arquivo principal)
   - Removida toda funcionalidade do Discord
   - Adicionada integração com Telegram Bot API
   - Novos campos de configuração para Bot Token e Chat ID
   - Atualizado para versão 2.0.0

2. **README.md**
   - Atualizada documentação para refletir integração com Telegram
   - Adicionado guia de configuração do Telegram
   - Atualizado diagrama de workflow
   - Adicionadas instruções para obter Bot Token e Chat ID

3. **INSTALLATION.md**
   - Substituído guia de setup do Discord por Telegram
   - Atualizadas opções de configuração
   - Novo troubleshooting para Telegram

4. **RELEASE_NOTES.md**
   - Adicionadas notas da versão 2.0.0
   - Documentadas todas as breaking changes
   - Incluído guia de migração

## 🔧 Configuração do Telegram

### Passo 1: Criar um Bot no Telegram

1. Abra o Telegram e procure por **@BotFather**
2. Envie o comando `/newbot`
3. Siga as instruções:
   - Escolha um nome para seu bot (ex: JSHunter Alerts)
   - Escolha um username (deve terminar com 'bot', ex: jshunter_alerts_bot)
4. O BotFather enviará seu **Bot Token**
   - Formato: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
   - **GUARDE ESTE TOKEN COM SEGURANÇA!**

### Passo 2: Obter o Chat ID

#### Opção A: Canal Privado/Público

1. Crie um canal no Telegram (ou use um existente)
2. Adicione seu bot ao canal como **administrador**
3. Envie uma mensagem qualquer no canal
4. Abra seu navegador e acesse:
   ```
   https://api.telegram.org/bot<SEU_BOT_TOKEN>/getUpdates
   ```
   Substitua `<SEU_BOT_TOKEN>` pelo token que você recebeu do BotFather

5. Procure pelo objeto `"chat"` no JSON retornado:
   ```json
   {
     "chat": {
       "id": -1001234567890,
       "title": "Meu Canal",
       "type": "channel"
     }
   }
   ```

6. Copie o valor do campo `"id"` (será um número negativo para canais)

#### Opção B: Grupo Privado

1. Crie um grupo no Telegram
2. Adicione seu bot ao grupo
3. Faça seu bot administrador do grupo
4. Envie uma mensagem no grupo
5. Acesse o mesmo link do passo anterior
6. Copie o `"id"` do chat (também será negativo)

#### Opção C: Chat Privado (DM)

1. Envie uma mensagem para o seu bot no Telegram
2. Acesse o link `https://api.telegram.org/bot<SEU_BOT_TOKEN>/getUpdates`
3. Copie o `"id"` do objeto `"chat"` (será um número positivo)

### Passo 3: Configurar a Extensão

1. Abra o Burp Suite
2. Vá para a aba **JSHunter**
3. Cole o **Bot Token** no campo "Telegram Bot Token"
4. Cole o **Chat ID** no campo "Telegram Chat ID"
5. Clique no botão **Test** ao lado do Chat ID
6. Você deve receber uma mensagem de teste no Telegram! 🎉
7. Marque a opção "Send findings to Telegram"

## 📊 Comparação: Discord vs Telegram

| Recurso | Discord (v1.0.0) | Telegram (v2.0.0) |
|---------|------------------|-------------------|
| Configuração | Webhook URL | Bot Token + Chat ID |
| Formato | Markdown Discord | Markdown Telegram |
| Emojis | ❌ Não | ✅ Sim (🔴/🟡) |
| Teste | Botão "Test Discord" | Botão "Test Telegram" |
| Privacidade | Servidor Discord | Bot próprio |
| API | Webhook simples | Bot API completa |

## 🎨 Novo Formato das Mensagens

### Secrets Verificados (🔴)
```
🔴 *[VERIFIED] Verified Secrets*
Found in: `https://example.com/script.js`

*GitHub Token*
```
ghp_1234567890abcdefghijklmnopqrstuvwxyz
```
Line: 42
```

### Secrets Não Verificados (🟡)
```
🟡 *[UNVERIFIED] Unverified Secrets*
Found in: `https://example.com/script.js`

*API Key*
```
api_key_1234567890abcdefghijklmnopqrstuvwxyz
```
Line: 15
```

## 🔍 Verificação de Configuração

### Testar Bot Token

Execute no navegador:
```
https://api.telegram.org/bot<SEU_BOT_TOKEN>/getMe
```

Resposta esperada:
```json
{
  "ok": true,
  "result": {
    "id": 123456789,
    "is_bot": true,
    "first_name": "JSHunter Alerts",
    "username": "jshunter_alerts_bot"
  }
}
```

### Testar Envio de Mensagem

Execute no navegador:
```
https://api.telegram.org/bot<SEU_BOT_TOKEN>/sendMessage?chat_id=<SEU_CHAT_ID>&text=Teste
```

Se funcionar, você receberá "Teste" no seu canal/grupo!

## ❓ Troubleshooting

### Erro: "Unauthorized"
- Verifique se o Bot Token está correto
- Certifique-se de que copiou o token completo

### Erro: "Chat not found"
- Verifique se o Chat ID está correto
- Certifique-se de que o bot foi adicionado ao canal/grupo
- Para canais, o ID deve ser negativo (ex: -1001234567890)

### Erro: "Bot was kicked from the channel"
- Adicione o bot novamente ao canal
- Certifique-se de que ele tem permissões de administrador

### Mensagem não chega
- Verifique se o bot é administrador do canal
- Teste enviando uma mensagem manual via API
- Verifique os logs no Burp Suite (aba JSHunter → Activity Log)

## 💡 Dicas

1. **Canais Separados**: Crie canais diferentes para:
   - Secrets verificados (críticos)
   - Secrets não verificados (informativos)
   - Logs de scan (debug)

2. **Múltiplos Bots**: Você pode criar vários bots para diferentes propósitos

3. **Grupos**: Use grupos para colaborar com sua equipe em tempo real

4. **Notificações**: Configure as notificações do Telegram para não perder achados importantes

## 🎯 Próximos Passos

Após configurar o Telegram:

1. **Teste a extensão**: Navegue em sites com JavaScript
2. **Verifique os resultados**: Confira a aba JSHunter no Burp Suite
3. **Monitore o Telegram**: Aguarde as notificações de secrets
4. **Ajuste as configurações**: Ative/desative recursos conforme necessário

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs na aba "Activity Log" do JSHunter
2. Teste a configuração usando os botões "Test"
3. Consulte a documentação: README.md e INSTALLATION.md
4. Reporte issues no GitHub

---

**Boa caçada de secrets! 🎯🔐**

