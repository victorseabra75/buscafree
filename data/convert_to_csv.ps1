# ==============================================================================
# Script de Conversao CNPJ -> CSV em data\preprocessed
# Sem filtro restritivo de extensao + Diagnostico de Pastas Vazias
# ==============================================================================

$BaseDir   = "C:\Users\victo\Desktop\BUSCACNPJ\data\raw"
$OutputDir = "C:\Users\victo\Desktop\BUSCACNPJ\data\preprocessed"

if (-not (Test-Path $OutputDir)) {
    New-Item -Path $OutputDir -ItemType Directory | Out-Null
}

# Dicionario de cabecalhos por categoria
$Headers = @{
    "Cnaes"            = "codigo;descricao"
    "Empresas"         = "cnpj_basico;razao_social;natureza_juridica;qualificacao_responsavel;capital_social;porte_empresa;ente_federativo_responsavel"
    "Estabelecimentos" = "cnpj_basico;cnpj_ordem;cnpj_dv;identificador_matriz_filial;nome_fantasia;situacao_cadastral;data_situacao_cadastral;motivo_situacao_cadastral;nome_cidade_exterior;pais;data_inicio_atividade;cnae_fiscal_principal;cnae_fiscal_secundaria;tipo_logradouro;logradouro;numero;complemento;bairro;cep;uf;municipio;ddd_1;telefone_1;ddd_2;telefone_2;ddd_fax;fax;correio_eletronico;situacao_especial;data_situacao_especial"
    "Motivos"          = "codigo;descricao"
    "Municipios"       = "codigo;descricao"
    "Naturezas"        = "codigo;descricao"
    "Paises"           = "codigo;descricao"
    "Qualificacoes"    = "codigo;descricao"
    "Simples"          = "cnpj_basico;opcao_simples;data_opcao_simples;data_exclusao_simples;opcao_mei;data_opcao_mei;data_exclusao_mei"
    "Socios"           = "cnpj_basico;identificador_socio;nome_socio;cnpj_cpf_socio;qualificacao_socio;data_entrada_sociedade;pais;representante_legal;nome_representante;qualificacao_representante;faixa_etaria"
}

$Latin1Encoding = [System.Text.Encoding]::GetEncoding("ISO-8859-1")
$Utf8Encoding   = New-Object System.Text.UTF8Encoding($false)

Write-Host "Verificando todas as pastas em raw...`n" -ForegroundColor Yellow

$AllDirs = Get-ChildItem -Path $BaseDir -Directory | Sort-Object Name

foreach ($dir in $AllDirs) {
    $dirName  = $dir.Name
    $category = $dirName -replace '\d+$', ''
    $outputCsv = Join-Path -Path $OutputDir -ChildPath "$dirName.csv"

    if (-not $Headers.ContainsKey($category)) {
        Write-Host "[!] Categoria '$category' ($dirName) nao reconhecida. Pulando..." -ForegroundColor Yellow
        continue
    }

    # 1. VERIFICA SE O ARQUIVO JA FOI CRIADO EM PREPROCESSED
    if ((Test-Path $outputCsv) -and ((Get-Item $outputCsv).Length -gt 0)) {
        Write-Host "[JA EXISTE] $dirName.csv ja esta pronto em preprocessed." -ForegroundColor Gray
        continue
    }

    # 2. PEGA OS ARQUIVOS BRUTOS DENTRO DA PASTA
    $rawFiles = Get-ChildItem -Path $dir.FullName -File

    if (-not $rawFiles -or $rawFiles.Count -eq 0) {
        Write-Host "[AVISO] Pasta '$dirName' em raw esta VAZIA! Nenhum arquivo bruto encontrado." -ForegroundColor Red
        continue
    }

    foreach ($file in $rawFiles) {
        Write-Host "[...] Processando $dirName ($($file.Name)) -> preprocessed\$dirName.csv ..." -ForegroundColor Cyan

        $headerText = $Headers[$category]
        $reader = $null
        $writer = $null
        $success = $false

        try {
            $reader = New-Object System.IO.StreamReader($file.FullName, $Latin1Encoding)
            $writer = New-Object System.IO.StreamWriter($outputCsv, $false, $Utf8Encoding)

            # Escreve cabecalho
            $writer.WriteLine($headerText)

            # Copia o conteudo em blocos de 64 KB
            $bufferSize = 64 * 1024
            $buffer = New-Object char[] $bufferSize

            while (($charsRead = $reader.Read($buffer, 0, $bufferSize)) -gt 0) {
                $writer.Write($buffer, 0, $charsRead)
            }

            $success = $true
        }
        catch {
            Write-Host "[ERRO] Falha ao processar $($file.Name): $_" -ForegroundColor Red
        }
        finally {
            if ($null -ne $reader) { $reader.Close(); $reader.Dispose() }
            if ($null -ne $writer) { $writer.Close(); $writer.Dispose() }

            if ($success) {
                Write-Host "[OK] Concluido: $dirName.csv gerado com sucesso!" -ForegroundColor Green
            } else {
                if (Test-Path $outputCsv) { Remove-Item -Path $outputCsv -Force }
            }
        }
    }
}

Write-Host "`nProcessamento concluido!" -ForegroundColor Green