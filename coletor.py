import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time

def extrair_resultados(soup, data_str):
    resultados = []
    horarios = ["PTM", "PT", "PTV", "PTN", "CORUJA"]
    
    for h3 in soup.find_all("h3"):
        titulo = h3.get_text(strip=True)
        
        tipo = next((horario for horario in horarios if horario in titulo), None)
        
        if tipo:
            p = h3.find_next("p")
            
            if p:
                linhas = p.get_text(separator="\n").split("\n")
                numeros = [linha.split("►")[1].strip() for linha in linhas if "►" in linha]
                
                while len(numeros) < 7:
                    numeros.append("")
                
                if "Aguardando resultados" not in titulo:
                    resultados.append([data_str, tipo] + numeros[:7])
    
    return resultados

def obter_resultados_do_bicho_entre_anos(inicio_ano=2021):
    data_inicio = datetime(inicio_ano, 1, 1)
    data_atual = datetime.now()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    with open("resultados_jogo_do_bicho.html", "w", encoding="utf-8") as file:
        file.write("""
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Resultados do Jogo do Bicho</title>
            <style>
                body { font-family: Arial, sans-serif; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { border: 1px solid black; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <h2>Resultados do Jogo do Bicho</h2>
            <table>
                <tr>
                    <th>DATA</th><th>TIPO</th><th>1º</th><th>2º</th><th>3º</th><th>4º</th><th>5º</th><th>6º</th><th>7º</th>
                </tr>
        """)
    
        contador = 0
        while data_inicio <= data_atual:
            data_formatada = data_inicio.strftime('%Y/%m/%d')
            url = f"https://portalbrasil.net/jogodobicho/{data_formatada}/resultado-do-jogo-do-bicho-deu-no-poste-de-hoje-{data_inicio.strftime('%d-%m-%Y')}/"
            
            print(f"Processando: {data_inicio.strftime('%d/%m/%Y')}...")
            
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    resultados = extrair_resultados(soup, data_inicio.strftime('%d/%m/%Y'))
                    
                    if resultados:
                        for linha in resultados:
                            file.write("<tr>" + "".join(f"<td>{col}</td>" for col in linha) + "</tr>\n")
                    else:
                        print(f"** Sem resultados claros para {data_inicio.strftime('%d/%m/%Y')}. **")
                elif response.status_code == 404:
                    print(f"Página não encontrada ({response.status_code}), aguardando 15 segundos...")
                    time.sleep(15)
                else:
                    print(f"Falha ao acessar a página {url}. Status: {response.status_code}")
            
            except Exception as e:
                print(f"Erro ao acessar {url}: {e}")
            
            data_inicio += timedelta(days=1)
            contador += 1
            
            if contador % 25 == 0:
                print("Aguardando 15 segundos para evitar bloqueios...")
                time.sleep(15)
    
        file.write("""
            </table>
        </body>
        </html>
        """)
    
    print("Arquivo HTML salvo como resultados.html")

obter_resultados_do_bicho_entre_anos(2021)
