#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import quote

class BuscadorNoticias:

    def __init__(self):
        self.noticias = []

        self.termos = [
            "escorpião",
            "escorpiões",
            "picada de escorpião",
            "acidente escorpiônico",
            "infestação de escorpiões",
            "soro antiescorpiônico"
        ]

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

        return any(
            n.get('titulo', '').strip().lower() ==
            titulo.strip().lower()
            for n in existentes
        )

    def limpar_html(self, texto):
        return re.sub('<.*?>', '', texto)

    def detectar_gravidade(self, texto):
        texto = texto.lower()

        graves = [
            'morte',
            'morre',
            'óbito',
            'uti',
            'grave',
            'fatal'
        ]

        moderadas = [
            'picada',
            'acidente',
            'escorpião',
            'escorpioes',
            'infestação'
        ]

        if any(p in texto for p in graves):
            return 'grave'

        if any(p in texto for p in moderadas):
            return 'moderada'

        return 'leve'

    def detectar_estado(self, texto):

        estados = {
            'SP': 'São Paulo',
            'PR': 'Paraná',
            'MG': 'Minas Gerais',
            'RJ': 'Rio de Janeiro',
            'GO': 'Goiás',
            'BA': 'Bahia',
            'MT': 'Mato Grosso',
            'MS': 'Mato Grosso do Sul',
            'SC': 'Santa Catarina',
            'RS': 'Rio Grande do Sul'
        }

        texto_lower = texto.lower()

        for uf, nome in estados.items():
            if nome.lower() in texto_lower or uf.lower() in texto_lower:
                return uf

        return 'Brasil'

    def buscar_google_rss(self):

        print("🔍 Buscando Google News RSS...")

        for termo in self.termos:

            try:

                termo_encoded = quote(termo)

                url = f'https://news.google.com/rss/search?q={termo_encoded}&hl=pt-BR&gl=BR&ceid=BR:pt-419'

                response = requests.get(url, timeout=20)

                root = ET.fromstring(response.content)

                itens = root.findall('.//item')

                for item in itens[:20]:

                    titulo = item.find('title').text.strip()
                    link = item.find('link').text.strip()

                    descricao = ''
                    desc = item.find('description')

                    if desc is not None:
                        descricao = self.limpar_html(desc.text)

                    texto_completo = f"{titulo} {descricao}".lower()

                    if 'horóscopo' in texto_completo:
                        continue

                    if self.ja_existe(titulo):
                        continue

                    noticia = {
                        'titulo': titulo,
                        'descricao': descricao,
                        'link': link,
                        'data': datetime.now().strftime('%d/%m/%Y'),
                        'tipo': 'alerta',
                        'gravidade': self.detectar_gravidade(texto_completo),
                        'fonte': 'Google News',
                        'estado': self.detectar_estado(texto_completo),
                        'cidade': 'Não identificado'
                    }

                    self.noticias.append(noticia)

                    print(f'✅ {titulo[:80]}')

            except Exception as e:
                print(f'❌ Erro no termo "{termo}": {e}')

    def salvar_noticias(self):

        existentes = self.carregar_existentes()

        for noticia in self.noticias:

            if not any(
                n['titulo'].lower() ==
                noticia['titulo'].lower()
                for n in existentes
            ):
                existentes.append(noticia)

        existentes = sorted(
            existentes,
            key=lambda x: datetime.strptime(
                x['data'],
                '%d/%m/%Y'
            ),
            reverse=True
        )

        with open('noticias.json', 'w', encoding='utf-8') as f:
            json.dump(
                existentes,
                f,
                ensure_ascii=False,
                indent=2
            )

        print(f'\n📰 Total salvo: {len(existentes)}')
        print(f'🆕 Novas notícias: {len(self.noticias)}')

    def executar(self):

        print('=' * 70)
        print('🦂 MONITOR DE ESCORPIÕES')
        print(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
        print('=' * 70)

        self.buscar_google_rss()

        self.salvar_noticias()

        print('=' * 70)
        print('✅ FINALIZADO')
        print('=' * 70)

if __name__ == "__main__":

    buscador = BuscadorNoticias()

    buscador.executar()
