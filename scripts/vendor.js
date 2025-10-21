// scripts/vendor.js

console.log("vendor.js carregado.");

// ----------------------------------------------------
// FAKE SECRET 3: AWS Access Key ID (formato que o TruffleHog detecta)
// A extensão deve detectar isso como um secret verificado.
// ----------------------------------------------------
const AWS_ACCESS_KEY = "AKIA9876543210FEDCBA"; // <<-- JSHunter deve encontrar isso

function connectToAWS() {
    console.log("Conectando à AWS com a chave:", AWS_ACCESS_KEY.substring(0, 7) + "...");
}

connectToAWS();


// ----------------------------------------------------
// FAKE SECRET 4: Slack Webhook URL (formato que o TruffleHog detecta)
// Isso é outro exemplo de secret não verificado.
// ----------------------------------------------------
let notificationConfig = {
    webhook: "https://hooks.slack.com/services/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ba",
    channel: "#alerts"
};

function loadNotificationConfig() {
    console.log("Configuração de notificações carregada.");
}

loadNotificationConfig();