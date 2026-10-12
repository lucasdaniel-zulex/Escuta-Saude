import pandas as pd
import requests
from zipfile import ZipFile
import io

# 1. Definir a URL do arquivo do Fala.BR 
# (Obtenha o link de download exato do ano desejado no portal dados.gov.br)
url = "LINK_DO_ARQUIVO_ZIP_DO_FALABR_AQUI" 

print("Baixando dados...")
response = requests.get(url)
zip_file = ZipFile(io.BytesIO(response.content))

# O ZIP geralmente contém um CSV. Pegamos o primeiro arquivo da lista.
csv_filename = zip_file.namelist()[0] 

# 2. Carregar no Pandas lidando com o padrão brasileiro (latin-1 e ponto e vírgula)
print("Carregando no Pandas...")
df = pd.read_csv(zip_file.open(csv_filename), sep=';', encoding='latin-1', low_memory=False)

# 3. Padronização
print("Limpando dados...")
# Remove espaços extras dos nomes das colunas e converte tudo para minúsculo
df.columns = df.columns.str.strip().str.lower()

# 4. Filtro Geográfico e Temático
# Filtrando para uma microrregião específica para não sobrecarregar o processamento
df_filtrado = df[(df['uf'] == 'SP') & (df['municipio'] == 'Sorocaba')]

# Filtrar apenas ocorrências onde o assunto principal envolve saúde
df_saude = df_filtrado[df_filtrado['assunto'].astype(str).str.contains('saúde|sus|hospital|médico|medicamento', case=False, na=False)]

# Remover linhas onde o texto da manifestação (a reclamação em si) está em branco
coluna_texto = 'resumo' # O nome exato varia por ano, pode ser 'resumo_manifestacao' ou 'texto'
if coluna_texto in df_saude.columns:
    df_saude = df_saude.dropna(subset=[coluna_texto])

# 5. Exportar o dado limpo
# JSON é o melhor formato para iterar nos pipelines de IA (como RAG ou Extração via LLaMA)
output_file = 'reclamacoes_saude_limpo.json'
df_saude.to_json(output_file, orient='records', force_ascii=False, indent=4)

print(f"Concluído! {len(df_saude)} registros salvos em {output_file}")