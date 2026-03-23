import os
import shutil
from pathlib import Path

# --- CONFIGURAÇÃO ---
PASTA_RAIZ = Path("/mnt/Edu")
PASTA_HD = PASTA_RAIZ / Path("backup/minhas imagens/2016/viagem/fotos videos camera do val/PRIVATE/AVCHD/BDMV/STREAM/") # Ajuste para o ponto de montagem do seu HD
DESTINO = Path("/home/edu/Vídeos/2016-06_CALIFORNIA_CAM_VAL")  # Pasta de destino para os arquivos copiados

# Cole sua lista de arquivos aqui (pode ser o caminho relativo que o 'find' deu)
ARQUIVOS_PARA_COPIAR = """
00019.MTS
00000.MTS
00001.MTS
00002.MTS
00003.MTS
00004.MTS
00005.MTS
00006.MTS
00007.MTS
00008.MTS
00009.MTS
00010.MTS
00011.MTS
00012.MTS
00013.MTS
00014.MTS
00015.MTS
00016.MTS
00017.MTS
00018.MTS
00020.MTS
00021.MTS
00022.MTS
00023.MTS
00024.MTS
00025.MTS
00026.MTS
00027.MTS
00028.MTS
00029.MTS
00030.MTS
00031.MTS
00032.MTS
00033.MTS
00034.MTS
00035.MTS
00036.MTS
00037.MTS
00038.MTS
00039.MTS
00040.MTS
00041.MTS
00042.MTS
00043.MTS
00044.MTS
00045.MTS
00046.MTS
00047.MTS
00048.MTS
00049.MTS
00050.MTS
00051.MTS
00052.MTS
"""

def iniciar_copia():
    # 1. Preparar destino
    DESTINO.mkdir(parents=True, exist_ok=True)
    
    # 2. Limpar lista
    lista = [a.strip() for a in ARQUIVOS_PARA_COPIAR.strip().split('\n') if a.strip()]
    
    print(f"📂 Destino: {DESTINO}")
    print(f"⏳ Preparando cópia de {len(lista)} arquivos...\n")

    for idx, item in enumerate(lista, 1):
        # Resolve o caminho: Se começar com './', ele anexa ao PASTA_HD
        origem = (PASTA_HD / item).resolve()
        
        # Nome formatado para o FastMerge (001, 002...)
        ext = origem.suffix
        novo_nome = f"{idx:03d}_{origem.name}"
        caminho_final = DESTINO / novo_nome

        if not origem.exists():
            print(f"❌ [ERRO] Não encontrado: {item}")
            continue

        print(f"🚚 [{idx}/{len(lista)}] Copiando: {origem.name} -> {novo_nome}...", end="\r")
        
        try:
            # shutil.copy2 preserva data de modificação e metadados originais
            shutil.copy2(origem, caminho_final)
            print(f"✅ [{idx}/{len(lista)}] Sucesso: {novo_nome}                    ")
        except Exception as e:
            print(f"❌ Erro ao copiar {origem.name}: {e}")

    print(f"\n✨ Processo finalizado. Agora é só rodar o FastMerge na pasta: {DESTINO}")

if __name__ == "__main__":
    iniciar_copia()