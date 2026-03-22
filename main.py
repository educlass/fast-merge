#!/usr/bin/env python3
"""
FastMerge - Merge múltiplos vídeos usando FFmpeg stream copy
Author: FastMerge Team
Date: 2026-03-22
"""

import os
import sys
import json
import re
import subprocess
import argparse
from pathlib import Path
from typing import List, Tuple


class FastMerge:
    """Classe principal para merge de vídeos usando FFmpeg"""
    
    SUPPORTED_EXTENSIONS = [
        '.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv',
        '.mts', '.m2ts', '.ts',  # AVCHD/MPEG Transport Stream
        '.mpg', '.mpeg', '.m4v', '.wmv', '.3gp', '.vob'
    ]
    
    def __init__(self, config_path: str = "config.json"):
        """Inicializa o FastMerge com configurações do JSON"""
        self.config = self._load_config(config_path)
        self.input_folder = Path(self.config.get("input_folder", "./input"))
        self.output_folder = Path(self.config.get("output_folder", "./output"))
        self.output_filename = self.config.get("output_filename", "video_final.mp4")
        self.cleanup = self.config.get("cleanup_temp_files", True)
        self.verbose = self.config.get("verbose", True)
        self.temp_manifest = Path("inputs.txt")
        
    def _load_config(self, config_path: str) -> dict:
        """Carrega configurações do arquivo JSON"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self._print_error(f"Arquivo de configuração '{config_path}' não encontrado!")
            sys.exit(1)
        except json.JSONDecodeError as e:
            self._print_error(f"Erro ao parsear JSON: {e}")
            sys.exit(1)
    
    def _print_info(self, message: str):
        """Imprime mensagem informativa"""
        if self.verbose:
            print(f"ℹ️  {message}")
    
    def _print_success(self, message: str):
        """Imprime mensagem de sucesso"""
        print(f"✅ {message}")
    
    def _print_error(self, message: str):
        """Imprime mensagem de erro"""
        print(f"❌ {message}", file=sys.stderr)
    
    def _print_warning(self, message: str):
        """Imprime mensagem de aviso"""
        print(f"⚠️  {message}")
    
    def _check_ffmpeg(self) -> bool:
        """Verifica se FFmpeg está instalado"""
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _natural_sort_key(self, filename: str) -> List:
        """
        Gera chave para ordenação natural (1, 2, 10 ao invés de 1, 10, 2)
        """
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split(r'(\d+)', filename)]
    
    def scan_videos(self) -> List[Path]:
        """
        Scanner: Varre a pasta de entrada em busca de arquivos de vídeo
        Smart Sort: Ordenação inteligente
        """
        if not self.input_folder.exists():
            self._print_error(f"Pasta de entrada '{self.input_folder}' não existe!")
            return []
        
        self._print_info(f"Escaneando pasta: {self.input_folder}")
        
        videos = []
        for file in self.input_folder.iterdir():
            if file.is_file() and file.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                videos.append(file)
        
        # Smart Sort - ordenação natural
        videos.sort(key=lambda x: self._natural_sort_key(x.name))
        
        if videos:
            self._print_success(f"Encontrados {len(videos)} vídeos:")
            for idx, video in enumerate(videos, 1):
                print(f"  {idx}. {video.name}")
        else:
            self._print_warning("Nenhum vídeo encontrado na pasta de entrada!")
        
        return videos
    
    def check_format_consistency(self, videos: List[Path]) -> Tuple[bool, str]:
        """
        Verifica se todos os vídeos têm o mesmo formato (codec, resolução, fps)
        """
        if len(videos) < 2:
            return True, "Apenas um vídeo encontrado"
        
        self._print_info("Verificando consistência de formatos...")
        
        video_info = []
        for video in videos:
            try:
                result = subprocess.run(
                    [
                        "ffprobe",
                        "-v", "error",
                        "-select_streams", "v:0",
                        "-show_entries", "stream=codec_name,width,height,r_frame_rate",
                        "-of", "json",
                        str(video)
                    ],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                data = json.loads(result.stdout)
                if data.get("streams"):
                    stream = data["streams"][0]
                    info = {
                        "file": video.name,
                        "codec": stream.get("codec_name"),
                        "width": stream.get("width"),
                        "height": stream.get("height"),
                        "fps": stream.get("r_frame_rate")
                    }
                    video_info.append(info)
            
            except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
                self._print_warning(f"Erro ao analisar {video.name}: {e}")
                return False, f"Erro ao analisar {video.name}"
        
        # Verifica se todos têm as mesmas propriedades
        if not video_info:
            return False, "Não foi possível obter informações dos vídeos"
        
        first = video_info[0]
        for info in video_info[1:]:
            if (info["codec"] != first["codec"] or 
                info["width"] != first["width"] or 
                info["height"] != first["height"] or
                info["fps"] != first["fps"]):
                
                msg = f"Inconsistência detectada: {info['file']} difere do primeiro vídeo"
                self._print_warning(msg)
                self._print_warning(f"  Primeiro: {first['codec']} {first['width']}x{first['height']} @ {first['fps']}")
                self._print_warning(f"  Atual: {info['codec']} {info['width']}x{info['height']} @ {info['fps']}")
                return False, msg
        
        self._print_success(f"Todos os vídeos têm o mesmo formato: {first['codec']} {first['width']}x{first['height']} @ {first['fps']}")
        return True, "OK"
    
    def generate_manifest(self, videos: List[Path]) -> bool:
        """
        Manifesto: Geração automática do arquivo inputs.txt para FFmpeg
        """
        self._print_info(f"Gerando manifesto: {self.temp_manifest}")
        
        try:
            with open(self.temp_manifest, 'w', encoding='utf-8') as f:
                for video in videos:
                    # Usa caminho absoluto para evitar problemas
                    abs_path = video.resolve()
                    # Escapa aspas simples no caminho
                    escaped_path = str(abs_path).replace("'", "'\\''")
                    f.write(f"file '{escaped_path}'\n")
            
            self._print_success(f"Manifesto criado com {len(videos)} entradas")
            return True
        
        except Exception as e:
            self._print_error(f"Erro ao criar manifesto: {e}")
            return False
    
    def merge_videos(self) -> bool:
        """
        The Merge: Execução do comando concat com -c copy
        """
        # Cria pasta de saída se não existir
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        output_path = self.output_folder / self.output_filename
        
        self._print_info(f"Iniciando merge para: {output_path}")
        self._print_info("Usando FFmpeg stream copy (sem re-renderização)...")
        
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", str(self.temp_manifest),
            "-c", "copy",
            "-movflags", "+faststart",  # YouTube-ready: move moov atom para o início
            "-y",  # Sobrescreve arquivo existente
            str(output_path)
        ]
        
        try:
            if self.verbose:
                # Mostra output do FFmpeg
                subprocess.run(cmd, check=True)
            else:
                # Silencioso
                subprocess.run(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True
                )
            
            self._print_success(f"Vídeo mesclado com sucesso: {output_path}")
            
            # Mostra tamanho do arquivo final
            size_mb = output_path.stat().st_size / (1024 * 1024)
            self._print_info(f"Tamanho do arquivo final: {size_mb:.2f} MB")
            self._print_info("🎬 Vídeo otimizado para YouTube (faststart enabled)")
            
            return True
        
        except subprocess.CalledProcessError as e:
            self._print_error(f"Erro ao executar FFmpeg: {e}")
            return False
    
    def cleanup_temp_files(self):
        """
        Cleanup: Remoção de arquivos temporários
        """
        if self.cleanup and self.temp_manifest.exists():
            self._print_info("Removendo arquivos temporários...")
            self.temp_manifest.unlink()
            self._print_success("Cleanup concluído")
    
    def run(self) -> bool:
        """
        Executa o pipeline completo de merge
        """
        print("=" * 60)
        print("🎥 FastMerge - Merge de Vídeos Ultra-Rápido")
        print("=" * 60)
        
        # 1. Verifica FFmpeg
        if not self._check_ffmpeg():
            self._print_error("FFmpeg não está instalado ou não está no PATH!")
            self._print_info("Instale com: sudo apt install ffmpeg (Ubuntu/Debian)")
            return False
        
        self._print_success("FFmpeg detectado")
        
        # 2. Scanner + Smart Sort
        videos = self.scan_videos()
        if not videos:
            return False
        
        # 3. Verificação de formato
        consistent, msg = self.check_format_consistency(videos)
        if not consistent:
            self._print_error("Os vídeos não podem ser mesclados com stream copy!")
            self._print_info("Considere re-codificar todos para o mesmo formato.")
            return False
        
        # 4. Gera manifesto
        if not self.generate_manifest(videos):
            return False
        
        # 5. The Merge
        success = self.merge_videos()
        
        # 6. Cleanup
        self.cleanup_temp_files()
        
        if success:
            print("=" * 60)
            print("🚀 Processo concluído com sucesso!")
            print("=" * 60)
        
        return success


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="FastMerge - Merge de vídeos ultra-rápido usando FFmpeg stream copy",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "-c", "--config",
        default="config.json",
        help="Caminho para o arquivo de configuração JSON (padrão: config.json)"
    )
    
    parser.add_argument(
        "-i", "--input",
        help="Sobrescreve a pasta de entrada do config.json"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Sobrescreve o nome do arquivo de saída do config.json"
    )
    
    args = parser.parse_args()
    
    # Cria instância do FastMerge
    merger = FastMerge(args.config)
    
    # Sobrescreve configurações se fornecidas via CLI
    if args.input:
        merger.input_folder = Path(args.input)
    if args.output:
        merger.output_filename = args.output
    
    # Executa
    success = merger.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
