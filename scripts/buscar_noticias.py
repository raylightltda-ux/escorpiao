#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

class BuscadorNoticias:
    def __init__(self):
        self.noticias = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
    
    def carregar_existentes(self):
        if os.path.exists('noticias.json'):
            try:
                with open('noticias.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def ja_existe(self, titulo):
        existentes = self.carregar_existentes()
        return any(n.get('titulo', '').lower() == titulo.lower() for n in existentes)
    
    def buscar_google_news(self):
        print("[1/3] 🔍 Buscando Google News...")
        try:
            url = "https://news.google.com/search?q=escorpi%C3%A3o%20Brasil&hl=pt-BR&gl=BR"
            response = requests.get(url, headers=self.headers, timeout=15)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for article in soup.find_all('a', {'data-n-url': True})[:15]:
                try:
                    titulo = article.get_text(strip=True)
                    link = article.get('data-n-url', '')
                    
                    if 'escorpi' in titulo.lower() and 'horósco' not in titulo.lower() and len(titulo) > 15:
                        if not self.ja_existe(titulo):
                            self.noticias.append({
                                'titulo': titulo,
                                'link': link if link.startswith('http') else 'https://news.google.com',
                                'data': datetime.now().strftime('%d/%m/%Y'),
                                'tipo': 'alerta',
                                'gravidade': 'moderada',
                                'fonte': 'Google News',
                                'descricao': titulo
                            })
                            print(f"  ✅ {titulo[:60]}...")
                except:
                    continue
        except Exception as e:
            print(f"  ❌ Erro: {e}")
    
    def buscar_g1(self):
        print("[2/3] 🔍 Buscando G1...")
        try:
            url = "https://g1.globo.com/busca/?q=escorpião"
            response = requests.get(url, headers=self.headers, timeout=15)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for link in soup.find_all('a', limit=15):
                try:
                    titulo = link.get_text(strip=True)
                    href = link.get('href', '')
                    
                    if 'escorpi' in titulo.lower() and 'horósco' not in titulo.lower() and len(titulo) > 15:
                        if not self.ja_existe(titulo):
                            self.noticias.append({
                                'titulo': titulo,
                                'link': href if href.startswith('http') else 'https://g1.globo.com',
                                'data': datetime.now().strftime('%d/%m/%Y'),
                                'tipo': 'alerta',
                                'gravidade': 'moderada',
                                'fonte': 'G1',
                                'descricao': titulo
                            })
                            print(f"  ✅ {titulo[:60]}...")
                except:
                    continue
        except Exception as e:
            print(f"  ❌ Erro: {e}")
    
    def buscar_agencia_brasil(self):
        print("[3/3] 🔍 Buscando Agência Brasil...")
        try:
            url = "https://agenciabrasil.ebc.com.br/geral?page=0"
            response = requests.get(url, headers=self.headers, timeout=15)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for link in soup.find_all('a', limit=20):
                try:
                    titulo = link.get_text(strip=True)
                    href = link.get('href', '')
                    
                    if 'escorpi' in titulo.lower() and 'horósco' not in titulo.lower() and len(titulo) > 15:
                        if not self.ja_existe(titulo):
                            self.noticias.append({
                                'titulo': titulo,
                                'link': href if href.startswith('http') else 'https://agenciabrasil.ebc.com.br',
                                'data': datetime.now().strftime('%d/%m/%Y'),
                                'tipo': 'incidente',
                                'gravidade': 'moderada',
                                'fonte': 'Agência Brasil',
                                'descricao': titulo
                            })
                            print(f"  ✅ {titulo[:60]}...")
                except:
                    continue
        except Exception as e:
            print(f"  ❌ Erro: {e}")
    
    def salvar_noticias(self):
        try:
            existentes = self.carregar_existentes()
            
            for noticia in self.noticias:
                if not any(n['titulo'] == noticia['titulo'] for n in existentes):
                    existentes.append(noticia)
            
            existentes.sort(key=lambda x: x.get('data', ''), reverse=True)
            
            with open('noticias.json', 'w', encoding='utf-8') as f:
                json.dump(existentes, f, ensure_ascii=False, indent=2)
            
            print(f"\n✅ {len(existentes)} notícias salvas!")
            print(f"📰 Novas: {len(self.noticias)}")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    def executar(self):
        print("=" * 70)
        print("🦂 MONITOR DE ESCORPIÕES - BUSCA AUTOMÁTICA")
        print(f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 70)
        
        self.buscar_google_news()
        self.buscar_g1()
        self.buscar_agencia_brasil()
        
        self.salvar_noticias()
        
        print("=" * 70)
        print("✅ BUSCA CONCLUÍDA!")
        print("=" * 70)

if __name__ == "__main__":
    buscador = BuscadorNoticias()
    buscador.executar()
