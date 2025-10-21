// Arquivo de teste com secrets mais realistas para o TruffleHog detectar

// AWS Access Key ID realista
const awsConfig = {
    accessKeyId: "AKIA1234567890ABCDEF",
    secretAccessKey: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY123",
    region: "us-east-1"
};

// GitHub Personal Access Token realista
const githubToken = "ghp_1234567890abcdef1234567890abcdef12345678";

// Stripe Secret Key realista
const stripeSecretKey = "sk_test_51H1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef";

// Generic API Key realista
const apiKey = "api_key_1234567890abcdef1234567890abcdef12345678";

// Database connection string
const dbConnection = "postgresql://user:password123@localhost:5432/database";

// JWT Token realista
const jwtToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c";

console.log("Configurações carregadas:", {
    aws: awsConfig.accessKeyId,
    github: githubToken.substring(0, 10) + "...",
    stripe: stripeSecretKey.substring(0, 10) + "...",
    api: apiKey.substring(0, 10) + "...",
    db: dbConnection.substring(0, 20) + "...",
    jwt: jwtToken.substring(0, 20) + "..."
});
