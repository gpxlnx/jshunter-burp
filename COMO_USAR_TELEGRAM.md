# 🚀 Como Configurar o Telegram - Guia Rápido

## ⚡ Configuração em 5 Minutos

### Passo 1: Criar o Bot (2 minutos)

1. Abra o **Telegram** no celular ou desktop
2. Procure por: `@BotFather`
3. Envie: `/newbot`
4. Digite o nome do bot: `JSHunter Alerts` (ou outro nome)
5. Digite o username: `jshunter_alerts_bot` (ou outro, deve terminar com "bot")
6. **COPIE E GUARDE O TOKEN** que aparece:
   ```
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

### Passo 2: Criar Canal e Obter Chat ID (2 minutos)

1. No Telegram, crie um **novo canal** (botão de menu → Novo Canal)
2. Nome do canal: `JSHunter Findings` (ou outro nome)
3. Escolha se será privado ou público
4. Após criar, clique em "Adicionar membros"
5. Procure pelo nome do seu bot (`jshunter_alerts_bot`)
6. Adicione o bot ao canal
7. Torne o bot **administrador** (clique no bot → ⋮ → Promover a Administrador)
8. Envie **qualquer mensagem** no canal (ex: "teste")

9. Abra seu navegador e acesse:
   ```
   https://api.telegram.org/bot123456789:ABCdefGHIjklMNOpqrsTUVwxyz/getUpdates
   ```
   ⚠️ **SUBSTITUA** o token pelo seu token real!

10. Você verá algo assim:
    ```json
    {
      "ok": true,
      "result": [{
        "message": {
          "chat": {
            "id": -1001234567890,
            "title": "JSHunter Findings",
            "type": "channel"
          }
        }
      }]
    }
    ```

11. **COPIE O ID** (o número negativo): `-1001234567890`

### Passo 3: Configurar no Burp Suite (1 minuto)

1. Abra o **Burp Suite**
2. Vá para a aba **JSHunter**
3. Cole o **Bot Token** no campo correspondente
4. Cole o **Chat ID** no campo correspondente
5. Clique no botão **Test**
6. Vá ao Telegram e veja se recebeu a mensagem de teste! 🎉

## ✅ Pronto! Agora é só usar

A partir de agora, sempre que o JSHunter encontrar secrets em arquivos JavaScript, você receberá notificações automáticas no seu canal do Telegram!

## 📱 Exemplo de Notificação

Quando um secret for encontrado, você receberá:

```
🔴 *[VERIFIED] Verified Secrets*
Found in: `https://example.com/app.js`

*AWS Access Key*
```
AKIAIOSFODNN7EXAMPLE
```
Line: 42
```

## 🔧 Troubleshooting Rápido

### ❌ "Unauthorized"
- Verifique se copiou o token completo
- Certifique-se de não ter espaços extras

### ❌ "Chat not found"
- Verifique se o bot foi adicionado ao canal
- Certifique-se de que o bot é administrador
- O Chat ID deve ser negativo para canais

### ❌ Não recebo mensagens
- Vá em Configurações do Canal → Administradores
- Verifique se o bot está lá
- Tente remover e adicionar o bot novamente

## 💡 Dicas

- **Canal Privado**: Recomendado para segurança
- **Múltiplos Canais**: Crie canais separados para verified/unverified
- **Notificações**: Configure no Telegram para não perder achados críticos
- **Mobile**: Receba alertas em tempo real no celular

## 📞 Precisa de Ajuda?

1. Confira o arquivo `MIGRATION_GUIDE.md` para guia completo
2. Veja `RESUMO_ALTERACOES.md` para entender todas as mudanças
3. Leia `README.md` para documentação completa

---

**Boa caçada! 🎯🔐**

