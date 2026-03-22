# 🎥 FastMerge

> **Proposta:** Unir múltiplos vídeos de forma quase instantânea para upload no YouTube, sem re-renderização e sem perda de qualidade.

---

## 💡 A Solução
Diferente de editores tradicionais (Kdenlive, Premiere) que processam cada frame novamente, o **FastMerge** utiliza o motor do **FFmpeg** no modo **Stream Copy**. 

Em vez de "desenhar" o vídeo de novo, nós apenas copiamos os pacotes de dados de um arquivo para o outro. Se os vídeos possuem o mesmo codec e resolução, o processo é limitado apenas pela velocidade de leitura/escrita do seu SSD.

## 🛠️ Estratégia Inicial
O projeto será um utilitário em **Python** seguindo este fluxo:

1. **Scanner:** Varre uma pasta de entrada em busca de arquivos de vídeo.
2. **Smart Sort:** Ordenação inteligente para garantir que `2.mp4` venha antes de `10.mp4`.
3. **Manifesto:** Geração automática do arquivo temporário `inputs.txt` exigido pelo FFmpeg.
4. **The Merge:** Execução do comando `concat` com a flag `-c copy`.
5. **Cleanup:** Remoção de arquivos temporários após a conclusão.
6. **all equals format** Garantir que na pasta existam arquivos no msm formato pra evitar erros de audio e video

## ⚠️ Gargalos e Validações
* **Inconsistência de Codec:** Se um vídeo for `1080p` e outro `4K`, ou se os FPS (frames por segundo) divergirem, o modo `copy` pode gerar artefatos ou falhar.
* **Ausência de Áudio:** Mesclar clipes com áudio e clipes mudos pode quebrar a sincronização do arquivo final.
* **Duração de Metadados:** Em alguns casos, o player pode exibir a duração errada se os timestamps dos arquivos originais estiverem corrompidos.

**✅ Solução Implementada:** O FastMerge verifica automaticamente se todos os vídeos possuem o mesmo codec, resolução e FPS antes de iniciar o merge, evitando erros.

## 🎬 Otimizações para YouTube

O FastMerge usa `-movflags +faststart` automaticamente, que:
- **Move o "moov atom"** (índice do vídeo) para o início do arquivo
- **Processamento mais rápido** no YouTube durante o upload
- **Streaming progressivo** - o vídeo pode começar a tocar antes de baixar completamente
- **Zero custo** - não adiciona tempo de processamento

## � Instalação

### Pré-requisitos
1. **Python 3.6+** instalado
2. **FFmpeg** instalado no sistema

```bash
# Ubuntu/Debian
sudo apt install ffmpeg python3

# Fedora
sudo dnf install ffmpeg python3

# Arch Linux
sudo pacman -S ffmpeg python

# macOS
brew install ffmpeg python3
```

### Clone o projeto
```bash
git clone <seu-repositorio>
cd fast-merge
```

## ⚙️ Configuração

O FastMerge usa um arquivo **`config.json`** para parametrização. Crie ou edite o arquivo:

```json
{
  "input_folder": "./meus_clips",
  "output_folder": "./output",
  "output_filename": "video_final.mp4",
  "cleanup_temp_files": true,
  "verbose": true
}
```

### Parâmetros do config.json

| Parâmetro | Tipo | Descrição | Padrão |
|-----------|------|-----------|---------|
| `input_folder` | string | Pasta contendo os vídeos a serem mesclados | `"./input"` |
| `output_folder` | string | Pasta onde o vídeo final será salvo | `"./output"` |
| `output_filename` | string | Nome do arquivo de vídeo final | `"video_final.mp4"` |
| `cleanup_temp_files` | boolean | Remove arquivos temporários após conclusão | `true` |
| `verbose` | boolean | Exibe informações detalhadas durante execução | `true` |

## 🚀 Como usar

### Uso básico (via config.json)
```bash
# 1. Configure o config.json com suas preferências
# 2. Coloque seus vídeos na pasta configurada (ex: ./meus_clips)
# 3. Execute:
python3 main.py
```

### Uso com parâmetros CLI
```bash
# Usando um arquivo de configuração diferente
python3 main.py --config meu_config.json

# Sobrescrevendo a pasta de entrada
python3 main.py --input ./outros_videos

# Sobrescrevendo o nome do arquivo final
python3 main.py --output meu_video_especial.mp4

# Combinando opções
python3 main.py --input ./clips --output resultado.mp4
```

## 📋 Funcionalidades Implementadas

### ✅ 1. Scanner Inteligente
Varre automaticamente a pasta de entrada em busca de arquivos de vídeo suportados:
- `.mp4`, `.mkv`, `.avi`, `.mov`, `.webm`, `.flv`

### ✅ 2. Smart Sort
Ordenação natural dos arquivos garantindo que `video2.mp4` venha antes de `video10.mp4`.

### ✅ 3. Validação de Formato
Antes do merge, verifica se todos os vídeos têm:
- Mesmo codec de vídeo
- Mesma resolução (largura x altura)
- Mesmo frame rate (FPS)

### ✅ 4. Geração Automática de Manifesto
Cria automaticamente o arquivo `inputs.txt` necessário para o FFmpeg no modo concat.

### ✅ 5. Stream Copy Mode
Usa o comando FFmpeg com `-c copy` para merge ultra-rápido sem re-renderização.

### ✅ 6. Cleanup Automático
Remove arquivos temporários após conclusão (configurável).

### ✅ 7. Configuração JSON
Toda a configuração é feita via arquivo JSON, facilitando reutilização e versionamento.

### ✅ 8. YouTube-Ready
Usa `-movflags +faststart` para otimizar vídeos para upload no YouTube - o processamento começa mais rápido!

## 🎯 Exemplo Prático

Imagine que você tem uma pasta com vários clipes de gameplay:

```
meus_clips/
├── 1.mp4
├── 2.mp4
├── 10.mp4
└── 15.mp4
```

**Problema:** Editores tradicionais podem levar horas para renderizar novamente.

**Solução com FastMerge:**

1. Configure o `config.json`:
```json
{
  "input_folder": "./meus_clips",
  "output_folder": "./output",
  "output_filename": "gameplay_completo.mp4"
}
```

2. Execute:
```bash
python3 main.py
```

3. **Resultado:** Vídeo mesclado em segundos (limitado apenas pela velocidade do SSD)! 🚀

## 🔍 Output de Exemplo

```
============================================================
🎥 FastMerge - Merge de Vídeos Ultra-Rápido
============================================================
✅ FFmpeg detectado
ℹ️  Escaneando pasta: meus_clips
✅ Encontrados 4 vídeos:
  1. 1.mp4
  2. 2.mp4
  3. 10.mp4
  4. 15.mp4
ℹ️  Verificando consistência de formatos...
✅ Todos os vídeos têm o mesmo formato: h264 1920x1080 @ 30/1
ℹ️  Gerando manifesto: inputs.txt
✅ Manifesto criado com 4 entradas
ℹ️  Iniciando merge para: output/gameplay_completo.mp4
ℹ️  Usando FFmpeg stream copy (sem re-renderização)...
✅ Vídeo mesclado com sucesso: output/gameplay_completo.mp4
ℹ️  Tamanho do arquivo final: 2547.83 MB
ℹ️  🎬 Vídeo otimizado para YouTube (faststart enabled)
ℹ️  Removendo arquivos temporários...
✅ Cleanup concluído
============================================================
🚀 Processo concluído com sucesso!
============================================================
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## 📄 Licença

Este projeto é open source. Use livremente! 🎉