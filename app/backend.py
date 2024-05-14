
from flask import Flask, request, render_template_string,render_template,flash,redirect,url_for, session
import requests
from unidecode import unidecode
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="PI",
    password="131297",
    database="Assaltos"
)

app = Flask(__name__)
app.secret_key = 'teste'

@app.route('/Paginainicial', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def reportincident():
    session.clear()
    if request.method == 'POST':
        nome = request.form.get('nome')
        rua = unidecode(request.form.get('rua').upper())
        bairro =  unidecode(request.form.get('bairro'))
        periodo = request.form.get('periodo')
        idade = request.form.get('idade')
        obs = request.form.get('obs')
        escolaridade = request.form.get('escolaridade')

        #verifica se o endereço digitado é valido
        UF = 'SP'
        #caso o usuario nao digite a rua, usa um valor padrao
        if rua == '' or len(rua) < 3:
            rua = 'teste'
        response = requests.get(f'https://viacep.com.br/ws/{UF}/diadema/{rua}/json/')
        data = response.json()
        #mostra o json recebido
        print(data)
        
        #verifica se o json recebido é vazio
        if not data:
            flash('Rua ou bairro inválido - OBS: Não digite o número da casa, apenas o nome da rua')
            session['nome'] = request.form.get('nome')
            session['rua'] = request.form.get('rua')
            session['bairro'] = request.form.get('bairro')
            session['periodo'] = request.form.get('periodo')
            session['idade'] = request.form.get('idade')
            session['obs'] = request.form.get('obs')
            session['escolaridade'] = request.form.get('escolaridade')
            nome = session.get('nome')
            rua = session.get('rua')
            bairro = session.get('bairro')
            periodo = session.get('periodo')
            idade = session.get('idade')
            obs = session.get('obs')
            escolaridade = session.get('escolaridade')      
        
        
        #verifica se o endereço digitado é igual ao endereço do json recebido
        elif unidecode(rua).upper() == unidecode(data[0]['logradouro'].upper()) and unidecode(bairro) == unidecode(data[0]['bairro']):
            flash('Endereço salvo com sucesso!', 'success')
            mycursor = db.cursor()
            sql = "INSERT INTO assaltos (nome, rua, bairro, periodo, idade, obs, escolaridade, data) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())"
            val = (nome, rua.upper(), bairro, periodo, idade, obs, escolaridade)
            mycursor.execute(sql, val)
            db.commit()
            print(mycursor.rowcount, "record inserted.")
            
        
        #caso o endereço digitado seja diferente do endereço do json recebido
        else:
            flash('Rua ou bairro inválido - OBS: Não digite o número da casa, apenas o nome da rua')
            session['nome'] = request.form.get('nome')
            session['rua'] = request.form.get('rua')
            session['bairro'] = request.form.get('bairro')
            session['periodo'] = request.form.get('periodo')
            session['idade'] = request.form.get('idade')
            session['obs'] = request.form.get('obs')
            session['escolaridade'] = request.form.get('escolaridade')
            nome = session.get('nome')
            rua = session.get('rua')
            bairro = session.get('bairro')
            periodo = session.get('periodo')
            idade = session.get('idade')
            obs = session.get('obs')
            escolaridade = session.get('escolaridade')      
        
   
    with open("static\HTML\PaginaInicial.html", encoding='utf-8') as file:
        template = file.read()
    return render_template_string(template, nome=session.get('nome', ''), rua=session.get('rua', ''), bairro=session.get('bairro', ''), periodo=session.get('periodo', ''), obs=session.get('obs', ''))

@app.route('/consulta', methods=['GET','POST'])
def consulta():
    mycursor = db.cursor()
    # Obter os parâmetros de consulta do request
    bairro = request.args.get('bairro')
    periodo = request.args.get('periodo')

    if bairro and periodo:
        # Se um bairro e um período foram fornecidos, use-os na consulta SQL
        query = "SELECT DISTINCT rua,bairro,periodo, COUNT(*) FROM assaltos WHERE bairro = %s AND periodo = %s GROUP BY rua, bairro, periodo"
        mycursor.execute(query, (bairro, periodo))
    elif bairro:
        # Se apenas um bairro foi fornecido, use-o na consulta SQL
        query = "SELECT DISTINCT rua,bairro,periodo, COUNT(*) FROM assaltos WHERE bairro = %s GROUP BY rua, bairro, periodo"
        mycursor.execute(query, (bairro,))
    elif periodo:
        # Se apenas um período foi fornecido, use-o na consulta SQL
        query = "SELECT DISTINCT rua,bairro,periodo, COUNT(*) FROM assaltos WHERE periodo = %s GROUP BY rua, bairro, periodo"
        mycursor.execute(query, (periodo,))
    else:
        # Se nenhum bairro ou período foram fornecidos, selecione todos os registros incluindo uma coluna de quantidade de vezes que o endereço foi registrado e deixe o que tiver mais registros em cima        
        query = "SELECT rua,bairro,periodo, COUNT(*) as quantidade FROM assaltos GROUP BY rua,bairro,periodo order by quantidade desc"
        mycursor.execute(query)
        
    dados = mycursor.fetchall()
    
    # Contar o total de casos
    query = "SELECT COUNT(*) FROM assaltos"
    mycursor.execute(query)
    total_casos = int(mycursor.fetchone()[0])
    
    #salva na variavel data_atualizacao a data salva no banco de dados da ultima linha convertendo para dd-mm-aaaa
    query = "SELECT data FROM assaltos ORDER BY data DESC LIMIT 1"
    mycursor.execute(query)
    data_atualizacao = mycursor.fetchone()[0]
    data_atualizacao = data_atualizacao.strftime('%d-%m-%Y')
    
    html_string = open("static\HTML\consulta.html", encoding='utf-8').read()
    return render_template_string(html_string, dados=dados, total_casos=total_casos, data_atualizacao=data_atualizacao)

@app.route('/quemSomos', methods=['GET','POST'])
def quemsomos():
    with open("static\HTML\quemsomos.html", encoding='utf-8') as file:
        template = file.read()
    return render_template_string(template)
  
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)