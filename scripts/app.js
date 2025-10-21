// scripts/app.js

console.log("app.js carregado.");

// ----------------------------------------------------
// FAKE SECRET 1: AWS Access Key ID (formato que o TruffleHog detecta)
// A extensão deve detectar isso como um secret verificado.
// ----------------------------------------------------
const AWS_CONFIG = {
    accessKeyId: "AKIA1234567890ABCDEF", // <<-- JSHunter deve encontrar isso
    secretAccessKey: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    region: "us-east-1"
};

function initializeAWS() {
    console.log("Inicializando SDK da AWS com a chave:", AWS_CONFIG.accessKeyId);
}

initializeAWS();


// ----------------------------------------------------
// FAKE SECRET 2: Slack Webhook URL (formato que o TruffleHog detecta)
// Isso é um exemplo de um secret não verificado.
// ----------------------------------------------------
const slackWebhook = "https://hooks.slack.com/services/T1234567890/B1234567890/abcdefghijklmnopqrstuvwx";

function setupNotifications() {
    console.log("Configurando notificações Slack:", slackWebhook);
}

setupNotifications();