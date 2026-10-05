# Instalação do Rclone no Windows via Winget
# Rode este script como Administrador no PowerShell

Write-Host "🚀 Iniciando setup de ferramentas no Windows..." -ForegroundColor Cyan

# 1. Instalar Rclone
if (!(Get-Command rclone -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Instalando Rclone via Winget..."
    winget install Rclone.Rclone --silent --accept-package-agreements --accept-source-agreements
    
    # Adiciona ao PATH da sessão atual para uso imediato
    $env:Path += ";C:\Program Files\Rclone"
    Write-Host "✅ Rclone instalado com sucesso!" -ForegroundColor Green
} else {
    Write-Host "✅ Rclone já está instalado." -ForegroundColor Green
}

# 2. Instalar Terraform (Opcional, mas recomendado)
if (!(Get-Command terraform -ErrorAction SilentlyContinue)) {
    Write-Host "📦 Instalando Terraform via Winget..."
    winget install HashiCorp.Terraform --silent
    Write-Host "✅ Terraform instalado!" -ForegroundColor Green
}

Write-Host "`n✨ Setup concluído! Por favor, reinicie seu VS Code/Terminal para atualizar o PATH." -ForegroundColor Yellow
