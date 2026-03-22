import os
import shutil
from pathlib import Path

# --- CONFIGURAÇÃO ---
PASTA_RAIZ = Path("/mnt/Edu")
PASTA_HD = PASTA_RAIZ / Path("Eduardo/Mae/Sitio - Videos/") # Ajuste para o ponto de montagem do seu HD
DESTINO = Path("/home/edu/Vídeos/sitio_mae")  # Pasta de destino para os arquivos copiados

# Cole sua lista de arquivos aqui (pode ser o caminho relativo que o 'find' deu)
ARQUIVOS_PARA_COPIAR = """
HPIM4312.AVI
HPIM4313.AVI
HPIM4314.AVI
HPIM4322.AVI
HPIM4325.AVI
HPIM4371.AVI
HPIM4378.AVI
HPIM4389.AVI
HPIM4390.AVI
HPIM4392.AVI
HPIM4395.AVI
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