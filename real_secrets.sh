#!/bin/bash
# Arquivo de configuração real com secrets que o TruffleHog deveria detectar

# GitHub Personal Access Token (formato real)
export GITHUB_TOKEN="ghp_1234567890abcdef1234567890abcdef12345678"

# AWS Credentials (formato real)
export AWS_ACCESS_KEY_ID="AKIA1234567890ABCDEF"
export AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# Stripe Secret Key (formato real)
export STRIPE_SECRET_KEY="sk_test_51H1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"

# Generic API Key (formato real)
export API_KEY="api_key_1234567890abcdef1234567890abcdef12345678"

# Database connection string
export DATABASE_URL="postgresql://user:password123@localhost:5432/database"

# JWT Secret
export JWT_SECRET="my-super-secret-jwt-key-12345"

# Slack Webhook URL
export SLACK_WEBHOOK="https://hooks.slack.com/services/T1234567890/B1234567890/abcdefghijklmnopqrstuvwx"

# SendGrid API Key
export SENDGRID_API_KEY="SG.abcdefghijklmnopqrstuvwx.1234567890abcdefghijklmnopqrstuvwx"

echo "Configurações carregadas com sucesso"
