#!/bin/bash
# Teste com secrets conhecidas que o TruffleHog deveria detectar

# GitHub Personal Access Token
export GITHUB_TOKEN="ghp_1234567890abcdef1234567890abcdef12345678"

# AWS Access Key
export AWS_ACCESS_KEY_ID="AKIA1234567890ABCDEF"
export AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# Stripe Secret Key
export STRIPE_SECRET_KEY="sk_test_51H1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"

# Generic API Key
export API_KEY="api_key_1234567890abcdef1234567890abcdef12345678"

echo "Configurações carregadas"
