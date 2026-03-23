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

### 🔊 Fallback de Áudio AAC

Por padrão (`force_audio_aac: true`), o FastMerge usa:
- **Vídeo:** Stream copy (ultra-rápido, sem re-renderização)
- **Áudio:** Conversão para AAC (192kbps)

**Por que isso é importante?**
- Arquivos `.AVI`, `.VOB` e outros formatos antigos frequentemente usam codecs de áudio incompatíveis com MP4 (PCM, mu-law, AC3, etc.)
- O AAC é universalmente compatível com MP4, YouTube, e todos os players modernos
- A conversão de áudio é **muito mais rápida** que re-renderizar o vídeo inteiro
- Você pode desativar com `"force_audio_aac": false` se todos os seus vídeos já usarem AAC

**⏱️ Tempo de processamento:**
- **Stream copy puro:** Limitado apenas pela velocidade do SSD (geralmente speed=50-100x)
- **Com conversão de áudio AAC:** Mais lento mas ainda rápido (speed=5-15x dependendo do CPU)
- **Com re-encode completo (`force_reencode: true`):** MUITO lento (speed=0.5-3x) - pode levar horas!
- **O FFmpeg mostra progresso em tempo real** - você verá frames processados, tempo e velocidade atualizando constantemente

## 🧠 Modo Smart - A Solução Inteligente (RECOMENDADO!)

**O problema:** Você tem vídeos do iPhone com resoluções diferentes e não quer esperar horas pelo re-encode...

**A solução:** O **Modo Smart** agrupa automaticamente os vídeos por resolução e cria um arquivo para cada grupo!

### Como Funciona

1. **Analisa todos os vídeos** e detecta resoluções únicas
2. **Agrupa por resolução** (1440x1080, 1280x960, 1920x1080, etc.)
3. **Detecta orientação** (portrait 📱 ou landscape 🖥️)
4. **Cria uma subpasta** para cada resolução
5. **Gera um vídeo** para cada grupo usando **stream copy ultra-rápido**!

### Vantagens

✅ **Ultra-rápido** - Usa stream copy (50-100x), não precisa re-codificar nada!  
✅ **Inteligente** - Agrupa automaticamente por resolução  
✅ **Mantém qualidade** - Zero perda de qualidade (stream copy)  
✅ **Mantém orientação** - Vídeos verticais continuam verticais 📱  
✅ **Detecta aspect ratio** - Identifica se vídeo é propositalmente vertical (9:16) ou horizontal (16:9)  
✅ **Lê metadados de rotação** - Considera tags de rotação da câmera para agrupar corretamente  
✅ **Organizado** - Cria subpastas por resolução  
✅ **Naming automático** - Inclui resolução no nome do arquivo  

### Como o FastMerge Decide a Orientação

O programa analisa **dois fatores** para determinar a orientação correta:

1. **Metadados de rotação** - Muitas câmeras (iPhone, Android) salvam tags `rotate=90` ou `rotate=270` no vídeo
2. **Aspect ratio (proporção)** - Calcula a relação largura/altura:
   - **< 0.75** (ex: 9:16 = 0.56) → Portrait intencional ✅ 📱 (Stories, Reels, TikTok)
   - **> 1.4** (ex: 16:9 = 1.77) → Landscape intencional ✅ 🖥️ (YouTube tradicional)
   - **Entre 0.75-1.4** (ex: 4:3, 3:4) → Zona ambígua ⚠️ (pode estar rotacionado por engano)

**Exemplo de análise:**
```
📊 Encontrados 3 grupos de resolução:
  🖥️  1920x1080 (landscape) - AR: 1.77 ✅
     5 vídeos
  📱 1080x1920 (portrait) - AR: 0.56 ✅ (2 com rotação)
     3 vídeos
  🖥️  640x480 (landscape) - AR: 1.33 ⚠️
     2 vídeos
```

**O que significa "com rotação"?**
- Vídeos com metadados `rotate=90` ou `270` são detectados
- Os metadados são **preservados** no arquivo final
- Players modernos (YouTube, VLC, Chrome) **respeitam automaticamente** essas tags
- O vídeo aparecerá corretamente orientado sem perda de qualidade!  

### Exemplo Prático

**Sua pasta:**
```
2016-06_edu/
├── IMG_0001.MOV  (1440x1080 landscape)
├── IMG_0002.MOV  (1280x960 landscape)
├── IMG_0003.MOV  (1440x1080 landscape)
├── IMG_0004.MOV  (1920x1080 portrait)  📱
└── IMG_0005.MOV  (1920x1080 portrait)  📱
```

**Config:**
```json
{
  "input_folder": "/home/edu/Vídeos/2016-06_edu",
  "output_folder": "/home/edu/Vídeos/2016-06_edu",
  "output_filename": "viagem.mp4",
  "smart_mode": true,
  "force_audio_aac": true
}
```

**Resultado:**
```
2016-06_edu/
├── 1440x1080/
│   └── viagem_1440x1080.mp4  ← 2 vídeos mesclados
├── 1280x960/
│   └── viagem_1280x960.mp4   ← 1 vídeo
└── 1920x1080/
    └── viagem_1920x1080.mp4  ← 2 vídeos portrait mesclados 📱
```

**Tempo de processamento:** ~1-2 minutos (ao invés de horas!)

### Como Ativar

```json
{
  "smart_mode": true
}
```

Pronto! O FastMerge faz o resto automaticamente. 🚀

### 📱 Vídeos em Pé vs Deitados - Como o FastMerge Decide?

**Problema comum:** Você grava vídeos no celular e alguns ficam "deitados" quando deveriam estar "em pé" (ou vice-versa).

**A solução do FastMerge:** Análise inteligente automática!

#### Como Funciona

O FastMerge analisa cada vídeo e determina:

1. **Lê os metadados da câmera** 
   - iPhones e Androids salvam uma tag `rotate=90` ou `rotate=270` quando você filma de lado
   - O FastMerge detecta isso e ajusta automaticamente!

2. **Calcula o aspect ratio (proporção)**
   - **9:16 (0.56)** → Claramente portrait intencional (Stories, Reels) 📱✅
   - **16:9 (1.77)** → Claramente landscape intencional (YouTube) 🖥️✅  
   - **4:3 ou 3:4** → Zona ambígua - pode estar errado ⚠️

3. **Agrupa corretamente**
   - Vídeos com mesma orientação REAL ficam juntos
   - Mesmo que o arquivo esteja "deitado", se tem metadados de rotação, o FastMerge sabe!

#### Exemplo Real

```
Seus vídeos:
├── video1.MOV (1080x1920 portrait) 📱
├── video2.MOV (1920x1080 landscape, mas rotate=90 nos metadados) 📱
└── video3.MOV (1920x1080 landscape) 🖥️
```

**O que o FastMerge faz:**
1. Detecta que `video2.MOV` tem `rotate=90`
2. Inverte as dimensões: 1920x1080 → 1080x1920
3. Agrupa `video1` e `video2` juntos (ambos portrait após rotação!)
4. `video3` fica sozinho (landscape real)

**Resultado final:**
- Os vídeos verticais ficam JUNTOS e em pé 📱
- Os vídeos horizontais ficam no grupo deles 🖥️
- YouTube e players modernos respeitam automaticamente!

#### E se o vídeo estiver errado mesmo?

Se o vídeo foi filmado realmente errado (sem metadados de rotação) e está fisicamente deitado:
- O FastMerge agrupa pela orientação física (como está o arquivo)
- Você terá um grupo `1080x1920` e outro `1920x1080`
- Assim você sabe quais vídeos estão cada orientação

#### Tabela de Aspect Ratios Comuns

| Resolução | Aspect Ratio | Tipo | Confiança | Uso Comum |
|-----------|--------------|------|-----------|-----------|
| 1080x1920 | 0.56 (9:16) | 📱 Portrait | ✅ Alta | Instagram Stories, Reels, TikTok |
| 720x1280 | 0.56 (9:16) | 📱 Portrait | ✅ Alta | Stories, vídeos verticais |
| 1920x1080 | 1.77 (16:9) | 🖥️ Landscape | ✅ Alta | YouTube, TV, cinema |
| 1280x720 | 1.77 (16:9) | 🖥️ Landscape | ✅ Alta | YouTube HD |
| 640x480 | 1.33 (4:3) | 🖥️ Landscape | ⚠️ Baixa | Câmeras antigas, pode estar errado |
| 480x640 | 0.75 (3:4) | 📱 Portrait | ⚠️ Baixa | Pode estar rotacionado incorretamente |

**Confiança Alta (✅):** FastMerge tem certeza da orientação intencional  
**Confiança Baixa (⚠️):** Pode estar rotacionado por engano - verifique os vídeos!

### 🔄 Modo Re-encode Completo (Para Vídeos Incompatíveis)

**⚠️ Atenção:** Antes de usar este modo lento, considere usar `smart_mode: true` que é muito mais rápido!

**Quando usar `force_reencode: true`:**
- ✅ Vídeos com **resoluções diferentes** (ex: 1440x1080 e 1280x960)
- ✅ Vídeos com **codecs diferentes** (H.264, MPEG-4, etc.)
- ✅ Vídeos com **FPS diferentes** (30fps, 60fps, etc.)
- ✅ Mix de vídeos de diferentes dispositivos (iPhone, Android, GoPro, etc.)

**⚠️ ATENÇÃO:**
- Este modo re-codifica TUDO (vídeo + áudio)
- É **MUITO mais lento** que stream copy (pode levar horas!)
- Use apenas quando os vídeos têm resolução/codec diferentes
- A qualidade final será excelente (CRF 23 = quase sem perda visível)

**Exemplo de configuração:**
```json
{
  "force_reencode": true,
  "target_resolution": "1920x1080"
}
```

**Resoluções recomendadas:**
- `"1920x1080"` - Full HD (YouTube padrão)
- `"1280x720"` - HD (mais rápido, arquivos menores)
- `"3840x2160"` - 4K (MUITO lento, para conteúdo premium)

### 📊 Comparação dos Modos

| Modo | Config | Velocidade | Quando usar |
|------|--------|-----------|-------------|
| **🧠 Smart** | `smart_mode: true` | ⚡⚡⚡ Ultra-rápido<br>(50-100x) | **RECOMENDADO!** Vídeos com resoluções diferentes - agrupa e processa separadamente |
| **Stream Copy Puro** | `force_audio_aac: false`<br>`smart_mode: false` | ⚡⚡⚡ Ultra-rápido<br>(50-100x) | Todos vídeos já são MP4/H.264 com AAC e mesma resolução |
| **Áudio AAC** | `force_audio_aac: true`<br>`smart_mode: false` | ⚡⚡ Rápido<br>(5-15x) | Vídeos compatíveis mas áudio antigo (PCM, mu-law, AC3) |
| **Re-encode Completo** | `force_reencode: true` | 🐌 Lento<br>(0.5-3x) | Último recurso - use smart_mode ao invés! |

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
  "verbose": true,
  "force_audio_aac": true,
  "force_reencode": false,
  "smart_mode": false,
  "target_resolution": "1920x1080"
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
| `force_audio_aac` | boolean | Força conversão do áudio para AAC (resolve codecs antigos como PCM/mu-law) | `true` || `smart_mode` | boolean | 🧠 **RECOMENDADO!** Agrupa vídeos por resolução e processa separadamente (ultra-rápido) | `false` || `force_reencode` | boolean | **⚠️ LENTO!** Re-codifica vídeo E áudio para resolver resoluções/codecs diferentes | `false` |
| `target_resolution` | string | Resolução alvo quando `force_reencode: true` (ex: "1920x1080", "1280x720") | `"1920x1080"` |

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

### ✅ 9. Progresso em Tempo Real
Mostra o progresso do FFmpeg durante o processamento para você saber que não travou!

### ✅ 10. Modo Re-encode para Vídeos Incompatíveis
Resolve automaticamente vídeos com resoluções/codecs diferentes (iPhone misto, etc.) - configura e deixa processando!

### ✅ 11. 🧠 Modo Smart (RECOMENDADO!)
Agrupa vídeos por resolução automaticamente e processa cada grupo separadamente - rápido e inteligente!

## 🎯 Exemplo Prático

### Cenário 1: Vídeos Compatíveis (Todos 1080p, H.264)

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
  "output_filename": "gameplay_completo.mp4",
  "force_audio_aac": true,
  "force_reencode": false
}
```

2. Execute:
```bash
python3 main.py
```

3. **Resultado:** Vídeo mesclado em segundos (limitado apenas pela velocidade do SSD)! 🚀

### Cenário 2: Vídeos do iPhone com Resoluções Diferentes

Você tem vídeos do iPhone que foram gravados em modos diferentes:

```
iphone_videos/
├── IMG_0001.MOV  (1440x1080 @ 15fps)
├── IMG_0002.MOV  (1280x960 @ 15fps)   ❌ Resolução diferente!
├── IMG_0003.MOV  (1440x1080 @ 15fps)
└── IMG_0004.MOV  (1920x1080 @ 30fps)  ❌ Resolução E FPS diferentes!
```

**Problema:** Stream copy não funciona devido às diferenças.

**Solução:**

```json
{
  "input_folder": "./iphone_videos",
  "output_folder": "./output",
  "output_filename": "iphone_completo.mp4",
  "force_reencode": true,           ← ATIVA RE-ENCODE
  "target_resolution": "1920x1080"  ← Normaliza tudo para Full HD
}
```

**⏱️ Tempo estimado:**
- 10 minutos de vídeo final = ~20-60 minutos de processamento (dependendo do CPU)
- Mas você pode deixar processando e fazer outra coisa! 🍕

## 🔍 Output de Exemplo

### Com Modo Smart (`smart_mode: true`) - RECOMENDADO!
```
============================================================
🎥 FastMerge - Merge de Vídeos Ultra-Rápido
🧠 Modo Smart Ativado
============================================================
✅ FFmpeg detectado
ℹ️  Escaneando pasta: /home/edu/Vídeos/2016-06_edu
✅ Encontrados 15 vídeos:
  1. IMG_0001.MOV
  2. IMG_0002.MOV
  ...
ℹ️  🧠 Modo Smart: Analisando resoluções...
✅ 📊 Encontrados 3 grupos de resolução:
  🖥️  1440x1080 (landscape): 8 vídeos
  🖥️  1280x960 (landscape): 5 vídeos
  📱 1920x1080 (portrait): 2 vídeos
ℹ️  🔄 Processando 3 grupos separadamente...

============================================================
🖥️  Grupo 1/3: 1440x1080 (landscape)
   8 vídeos
============================================================
ℹ️  📁 Pasta de saída: /home/edu/Vídeos/2016-06_edu/1440x1080
ℹ️  📄 Arquivo: 2016-06_viagem_cortes_1440x1080.mp4
ℹ️  ⚡ Usando stream copy (vídeo) + AAC (áudio)

⏳ Processando...
────────────────────────────────────────────────────────────
[FFmpeg progresso em tempo real]
────────────────────────────────────────────────────────────

✅ Criado: /home/edu/Vídeos/2016-06_edu/1440x1080/2016-06_viagem_cortes_1440x1080.mp4
ℹ️  📊 Tamanho: 856.32 MB

============================================================
🖥️  Grupo 2/3: 1280x960 (landscape)
   5 vídeos
============================================================
[... processamento similar ...]

============================================================
📱 Grupo 3/3: 1920x1080 (portrait)
   2 vídeos
============================================================
[... processamento similar ...]

============================================================
🎉 TODOS OS GRUPOS PROCESSADOS COM SUCESSO!
============================================================

📂 Arquivos gerados:
  ✅ /home/edu/Vídeos/2016-06_edu/1440x1080/2016-06_viagem_cortes_1440x1080.mp4
  ✅ /home/edu/Vídeos/2016-06_edu/1280x960/2016-06_viagem_cortes_1280x960.mp4
  ✅ /home/edu/Vídeos/2016-06_edu/1920x1080/2016-06_viagem_cortes_1920x1080.mp4
```

### Com stream copy puro (`force_audio_aac: false`, `smart_mode: false`)
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
ℹ️  ⚡ Modo stream copy puro - será muito rápido!
ℹ️  Usando FFmpeg stream copy puro (sem re-renderização)

⏳ Processando... (acompanhe o progresso abaixo)
────────────────────────────────────────────────────────────
[FFmpeg mostra progresso em tempo real aqui]
frame= 1234 fps=2500 q=-1.0 Lsize=  2547MB time=00:15:04.54 bitrate=21301.9kbits/s speed=83.3x
────────────────────────────────────────────────────────────

✅ Vídeo mesclado com sucesso: output/gameplay_completo.mp4
ℹ️  Tamanho do arquivo final: 2547.83 MB
ℹ️  🎬 Vídeo otimizado para YouTube (faststart enabled)
ℹ️  Removendo arquivos temporários...
✅ Cleanup concluído
============================================================
🚀 Processo concluído com sucesso!
============================================================
```

### Com conversão de áudio AAC (`force_audio_aac: true`)
```
ℹ️  Iniciando merge para: output/video_antigo.mp4
⚠️  ⏱️  Modo com conversão de áudio - pode levar alguns minutos
ℹ️  Usando stream copy para vídeo + re-encode AAC para áudio
ℹ️  (Garante compatibilidade com codecs antigos como PCM/mu-law)

⏳ Processando... (acompanhe o progresso abaixo)
────────────────────────────────────────────────────────────
[FFmpeg converte áudio e mostra progresso: frame, tempo, speed]
frame=15420 fps=180 q=-1.0 size=  1024MB time=00:08:34.20 bitrate=16289.2kbits/s speed=6.0x
────────────────────────────────────────────────────────────

✅ Vídeo mesclado com sucesso
ℹ️  ✨ Áudio convertido para AAC (compatível com todos os players)
```

## 🔧 Troubleshooting

### Erro: "Inconsistência detectada" - Resoluções diferentes

**Problema:** Vídeos têm resoluções diferentes (ex: 1440x1080 vs 1280x960)

**Causa comum:** 
- Vídeos do iPhone/Android gravados em modos diferentes (normal, slow-motion, foto vs vídeo)
- Mix de vídeos de diferentes dispositivos
- Alguns vídeos editados/recortados

**Solução 1 (RECOMENDADA):** Ative o modo smart no [config.json](config.json):
```json
{
  "smart_mode": true
}
```

Isso agrupa os vídeos por resolução e cria um arquivo para cada grupo - **ultra-rápido!**

**Solução 2 (LENTA):** Force re-encode de tudo:
```json
{
  "force_reencode": true,
  "target_resolution": "1920x1080"
}
```

**⚠️ Importante:** Re-encode será MUITO mais lento (horas) - prefira smart_mode!

### O programa parece travado / não mostra progresso?

**Não se preocupe!** Se `verbose: true` está ativo, o FFmpeg mostra progresso em tempo real:
- Procure linhas atualizando com `frame=`, `time=`, `speed=`
- O valor `speed=` indica quantas vezes mais rápido que tempo real está processando
  - `speed=50x` = 1 hora de vídeo processada em ~1 minuto
  - `speed=6x` = 1 hora de vídeo processada em ~10 minutos

**Dica:** Aguarde alguns segundos - o FFmpeg pode levar um tempo para iniciar, especialmente com arquivos grandes.

### Erro: "codec not currently supported in container"

Se você encontrar este erro com arquivos `.AVI`, `.VOB` ou formatos antigos:

**Solução 1 (Recomendada):** Ative o fallback de áudio AAC no [config.json](config.json):
```json
{
  "force_audio_aac": true
}
```

**Solução 2:** Veja o log detalhado do FFmpeg (ativado automaticamente) para identificar qual codec está causando o problema.

### Debug de Codecs

Para verificar o codec de áudio de um vídeo específico:
```bash
ffprobe -v error -select_streams a:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 seu_video.avi
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## 📄 Licença

Este projeto é open source. Use livremente! 🎉