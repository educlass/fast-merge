import os
import shutil
from pathlib import Path

# --- CONFIGURAÇÃO ---
PASTA_RAIZ = Path("/mnt/Edu")
PASTA_HD = PASTA_RAIZ / Path("backup/minhas imagens/2016/viagem/iphone/2016-06/") # Ajuste para o ponto de montagem do seu HD
DESTINO = Path("/home/edu/Vídeos/2016-06_CALIFORNIA_CEL_2")  # Pasta de destino para os arquivos copiados

# Cole sua lista de arquivos aqui (pode ser o caminho relativo que o 'find' deu)
ARQUIVOS_PARA_COPIAR = """
IMG_0823.MOV
IMG_0932.MOV
IMG_0952.MOV
IMG_0986.MOV
IMG_1028.MOV
IMG_0773.MOV
IMG_0774.MOV
IMG_0775.MOV
IMG_0777.MOV
IMG_0778.MOV
IMG_0783.MOV
IMG_0793.MOV
IMG_0794.MOV
IMG_0798.MOV
IMG_0799.MOV
IMG_0801.MOV
IMG_0802.MOV
IMG_0803.MOV
IMG_0804.MOV
IMG_0805.MOV
IMG_0806.MOV
IMG_0807.MOV
IMG_0808.MOV
IMG_0809.MOV
IMG_0810.MOV
IMG_0811.MOV
IMG_0812.MOV
IMG_0816.MOV
IMG_0817.MOV
IMG_0820.MOV
IMG_0821.MOV
IMG_0822.MOV
IMG_0824.MOV
IMG_0847.MOV
IMG_0848.MOV
IMG_0849.MOV
IMG_0850.MOV
IMG_0856.MOV
IMG_0857.MOV
IMG_0861.MOV
IMG_0862.MOV
IMG_0863.MOV
IMG_0865.MOV
IMG_0866.MOV
IMG_0867.MOV
IMG_0868.MOV
IMG_0869.MOV
IMG_0870.MOV
IMG_0871.MOV
IMG_0879.MOV
IMG_0884.MOV
IMG_0887.MOV
IMG_0888.MOV
IMG_0889.MOV
IMG_0891.MOV
IMG_0896.MOV
IMG_0897.MOV
IMG_0898.MOV
IMG_0899.MOV
IMG_0924.MOV
IMG_0925.MOV
IMG_0931.MOV
IMG_0933.MOV
IMG_0934.MOV
IMG_0935.MOV
IMG_0948.MOV
IMG_0949.MOV
IMG_0950.MOV
IMG_0951.MOV
IMG_0953.MOV
IMG_0955.MOV
IMG_0956.MOV
IMG_0957.MOV
IMG_0958.MOV
IMG_0959.MOV
IMG_0960.MOV
IMG_0961.MOV
IMG_0964.MOV
IMG_0966.MOV
IMG_0967.MOV
IMG_0980.MOV
IMG_0981.MOV
IMG_0982.MOV
IMG_0984.MOV
IMG_0985.MOV
IMG_0987.MOV
IMG_0988.MOV
IMG_0989.MOV
IMG_0990.MOV
IMG_0991.MOV
IMG_0992.MOV
IMG_0993.MOV
IMG_0994.MOV
IMG_0995.MOV
IMG_0996.MOV
IMG_0997.MOV
IMG_1008.MOV
IMG_1009.MOV
IMG_1019.MOV
IMG_1020.MOV
IMG_1021.MOV
IMG_1022.MOV
IMG_1023.MOV
IMG_1024.MOV
IMG_1029.MOV
IMG_1030.MOV
IMG_1031.MOV
IMG_1032.MOV
IMG_1033.MOV
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