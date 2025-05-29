from flask import Flask, render_template_string, jsonify, request, send_file, url_for
from markupsafe import escape, Markup
import os
import qrcode
from io import BytesIO
import base64
from datetime import datetime, timedelta
import uuid
import unicodedata

from flask_mail import Mail, Message
from fpdf import FPDF

app = Flask(__name__)

def escapejs_filter(value):
    return str(escape(value))

app.jinja_env.filters['escapejs'] = escapejs_filter

app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'SEU_EMAIL_GMAIL@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'SUA_SENHA_DE_APP_GMAIL')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', f'"Zelar +" <{os.environ.get("MAIL_USERNAME", "SEU_EMAIL_GMAIL@gmail.com")}>')


mail = Mail(app)

EMPRESA_NOME = "Zelar +"
EMPRESA_CIDADE = "SAO PAULO"
EMPRESA_LOGO_FILENAME = "logoloja.jpeg"
EMPRESA_MISSAO = "Promover uma melhoria na saúde, bem-estar e qualidade de vida por meio de alimentos saudáveis, acessíveis e com saborosos. Contribuindo para a formação de hábitos alimentares conscientes."
EMPRESA_VISAO = "Ser reconhecida nacionalmente como referência em alimentação saudável, inovadora e acessível, transformando a maneira como as pessoas se alimentam e cuidam da sua saúde."

PRODUTOS = [
    {"id": 1, "nome": "Marmita de suino (800g)", "preco": 37.94, "imagem": "imagem1.jpeg", "descricao": "Refeição prática, leve e saborosa. Lombo suíno assado, vagem cozida e purê de batata inglesa, em uma combinação sem glúten e sem lactose. Ideal para o dia a dia, com ingredientes selecionados e sabor caseiro."},
    {"id": 2, "nome": "Marmita de frango (800g)", "preco": 28.56, "imagem": "imagem2.jpeg", "descricao": "Uma refeição saudável, saborosa e prática para qualquer momento. Cubos de frango assado, acompanhados de arroz temperado e brócolis cozido no vapor. Sem glúten e sem lactose, é ideal para quem busca uma alimentação equilibrada no dia a dia."},
    {"id": 3, "nome": "Bebida Gaseificada (250ml)", "preco": 4.49, "imagem": "imagem3.jpeg", "descricao": "Refrescante e leve, essa bebida gaseificada com um toque natural de limão é perfeita para qualquer momento do dia. Sem glúten e sem lactose, ideal para acompanhar suas refeições ou refrescar-se a qualquer hora."},
    {"id": 4, "nome": "Achocolatado (450ml)", "preco": 8.97, "imagem": "imagem4.jpeg", "descricao": "Delicie-se com o sabor do chocolate em uma bebida leve e cremosa, perfeita para qualquer hora do dia. Sem glúten e sem lactose, é ideal para quem busca sabor e cuidado com a alimentação."},
    {"id": 5, "nome": "Alcaçuz (150ml)", "preco": 12.39, "imagem": "imagem5.jpeg", "descricao": "Desfrute do autêntico sabor do alcaçuz com nossos Doces de Alcaçuz. Totalmente sem glúten e sem lactose, são perfeitos para quem busca um mimo delicioso que se encaixa em qualquer dieta."},
    {"id": 6, "nome": "Chocolate (150g)", "preco": 7.61, "imagem": "imagem7.jpeg", "descricao": "Experimente a indulgência da nossa Barrinha de Chocolate. Deliciosamente rica e feita para todos, é sem glúten e sem lactose. O mimo perfeito para qualquer hora!"},
    {"id": 7, "nome": "Shake Pronto (350ml) sabor chocolate", "preco": 10.84, "imagem": "imagem9.jpeg", "descricao": "Uma refeição completa, prática e saborosa em embalagem pronta para beber. Esse shake nutritivo sabor chocolate é ideal para quem busca energia, saciedade e equilíbrio alimentar no dia a dia. Sem glúten e sem lactose, perfeito para dietas restritivas ou para quem deseja uma opção leve e funcional."},
    {"id": 8, "nome": "Shake em pó (350ml) sabor baunilha", "preco": 7.61, "imagem": "imagem8.jpeg", "descricao": "Substitua uma refeição completa de forma prática e saborosa. Este shake em pó sabor baunilha é ideal para quem busca nutrição equilibrada com facilidade. Basta diluir em água e consumir onde e quando quiser."},
    {"id": 9, "nome": "Salgadinho de Milho (400g)", "preco": 8.87, "imagem": "imagem6.jpeg", "descricao": "Delicioso, leve e crocante! Esse salgadinho de milho com cenoura é perfeito para o seu lanche do dia a dia, trazendo sabor e praticidade sem abrir mão do cuidado com a alimentação."},
    {"id": 10, "nome": "Salgadinho de Milho com Cenoura (400g)", "preco": 9.24, "imagem": "imagem12.jpeg", "descricao": "Delicioso, leve e crocante! Esse salgadinho de milho com cenoura é perfeito para o seu lanche do dia a dia, trazendo sabor e praticidade sem abrir mão do cuidado com a alimentação."},
    {"id": 11, "nome": "Barrinha de Castanha (60g)", "preco": 4.87, "imagem": "imagem11.jpeg", "descricao": "Uma opção prática, saudável e cheia de energia para o seu dia! Nossa barrinha de castanhas combina crocância e sabor natural, perfeita para levar na bolsa, no trabalho ou no treino."},
    {"id": 12, "nome": "Barrinha de Flocos de Arroz com Aveia (60g)", "preco": 3.63, "imagem": "imagem10.jpeg", "descricao": "Nossa Barrinha de Flocos de Arroz com Aveia é o snack perfeito para quem busca bem-estar. Sem glúten e sem lactose, combina a leveza dos flocos de arroz com a energia da aveia. Crocante e deliciosa, é ideal para qualquer hora do dia."},
    {"id": 13, "nome": "Biscoito de Arroz (12g)", "preco": 5.30, "imagem": "imagem13.jpeg", "descricao": "Descubra nosso Biscoito de Arroz, a opção perfeita para um snack leve e crocante. Naturalmente sem glúten e sem lactose, ele é ideal para todos os momentos."},
    {"id": 14, "nome": "Cookie (80g)", "preco": 11.40, "imagem": "imagem14.jpeg", "descricao": "Experimente o sabor irresistível do nosso Cookie. Crocante por fora e macio por dentro, ele é feito para todos, pois é sem glúten e sem lactose. O mimo perfeito para qualquer hora do dia!"}
]

CHAVE_PIX_REAL = "deolaevelyn14@gmail.com"

def formatar_texto_pix(texto, tamanho_max):
    nfkd_form = unicodedata.normalize('NFKD', str(texto))
    texto_sem_acento = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    texto_limpo = ''.join(filter(lambda char: char.isalnum() or char.isspace(), texto_sem_acento))
    texto_final = texto_limpo.strip()[:tamanho_max].upper()
    return texto_final

def gerar_pix_payload(chave_pix, valor, nome_beneficiario, cidade_beneficiario, txid=None):
    if txid is None:
        txid = str(uuid.uuid4()).replace('-', '')[:25]
    else:
        txid = ''.join(filter(str.isalnum, txid))[:25]

    nome_beneficiario_fmt = formatar_texto_pix(nome_beneficiario, 25)
    cidade_beneficiario_fmt = formatar_texto_pix(cidade_beneficiario, 15)

    payload_fields = {
        "00": "01",
        "26": [
            f"0014BR.GOV.BCB.PIX",
            f"01{len(chave_pix):02d}{chave_pix}"
        ],
        "52": "0000",
        "53": "986",
    }

    if valor > 0:
        payload_fields["54"] = f"{valor:.2f}"

    payload_fields.update({
        "58": "BR",
        "59": nome_beneficiario_fmt,
        "60": cidade_beneficiario_fmt,
        "62": [
            f"05{len(txid):02d}{txid}"
        ]
    })

    payload_string = ""
    for field_id, value_data in payload_fields.items():
        if isinstance(value_data, list):
            nested_content = "".join(value_data)
            payload_string += f"{field_id}{len(nested_content):02d}{nested_content}"
        else:
            payload_string += f"{field_id}{len(value_data):02d}{value_data}"

    payload_string += "6304"

    def crc16_ccitt_false(data_str: str):
        crc = 0xFFFF
        for byte in data_str.encode('ascii'):
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc <<= 1
        return crc & 0xFFFF

    crc_value = crc16_ccitt_false(payload_string[:-4])
    return f"{payload_string[:-4]}{crc_value:04X}"


def gerar_boleto_pdf_simulado(valor, nome_cliente, email_cliente, nome_empresa, num_pedido):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    try:
        logo_path = os.path.join(app.static_folder, 'images', EMPRESA_LOGO_FILENAME)
        if os.path.exists(logo_path):
             pdf.image(logo_path, x=10, y=8, w=30)
    except Exception as e:
        print(f"Erro ao carregar logo para PDF: {e}")
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Boleto Bancário Simulado - {nome_empresa}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Beneficiário: {nome_empresa}", ln=True)
    pdf.cell(0, 10, f"Pagador: {nome_cliente} ({email_cliente})", ln=True)
    pdf.cell(0, 10, f"Número do Pedido: {num_pedido}", ln=True)
    pdf.cell(0, 10, f"Data de Emissão: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.cell(0, 10, f"Data de Vencimento: {(datetime.now() + timedelta(days=5)).strftime('%d/%m/%Y')}", ln=True)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Valor do Documento: R$ {valor:.2f}".replace('.',','), ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    linha_digitavel_simulada = f"00190.00009 01022.78901{str(int(valor*10))[-1]} {uuid.uuid4().hex[:10].upper()}1 00000{int(valor*100):010d}"
    pdf.cell(0, 10, f"Linha Digitável: {linha_digitavel_simulada}", ln=True)
    pdf.ln(5)
    pdf.set_fill_color(0, 0, 0)
    y_pos_barcode = pdf.get_y()
    if y_pos_barcode + 25 > 277:
        pdf.add_page()
        y_pos_barcode = pdf.get_y()
    pdf.rect(x=10, y=y_pos_barcode, w=180, h=20, style='F')
    pdf.ln(25)
    pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 5, "Este é um boleto de demonstração e não possui valor real. Gerado para fins de teste do sistema de e-commerce da Zelar +.", align='C')
    boleto_bytes = BytesIO()
    pdf_output = pdf.output(dest='S').encode('latin-1')
    boleto_bytes.write(pdf_output)
    boleto_bytes.seek(0)
    return boleto_bytes

# MODIFICADO: Adicionado link "Meus Pedidos" no Navbar e CSS para responsividade
HTML_BASE_STRUCTURE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ nome_empresa }} - {{ page_title }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background-color: #f8f9fa; 
            color: #333; 
            display: flex; 
            flex-direction: column; 
            min-height: 100vh; 
            font-size: 1rem; /* Base font size */
        }
        .navbar-brand img.logo { max-height: 35px; margin-right: 8px; } /* Ajuste para mobile */
        .navbar-brand span { color: #28a745 !important; font-weight: bold; font-size: 1.3rem; vertical-align: middle;} /* Ajuste para mobile */
        .nav-link { font-size: 0.95rem; } /* Ajuste para mobile */
        .nav-link:hover, .nav-link.active { color: #28a745 !important; }
        .btn-primary, .btn-success { background-color: #28a745; border-color: #28a745; }
        .btn-primary:hover, .btn-success:hover { background-color: #218838; border-color: #1e7e34; }
        .card { border: 1px solid #e0e0e0; transition: box-shadow 0.3s ease-in-out; }
        .card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .card-title { color: #28a745; font-weight: 600; font-size: 1.1rem; }
        .section-title { color: #28a745; margin-bottom: 1.5rem; font-weight: 600; font-size: 1.8rem; }
        .footer { background-color: #343a40; color: white; padding: 2rem 0; margin-top: auto; font-size: 0.9rem;}
        .hero-section { background: linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.3)), url('https://images.unsplash.com/photo-1540420773420-3366772f4999?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80'); background-size: cover; background-position: center; color: white; padding: 3rem 0; text-align: center; } /* Padding ajustado */
        .hero-section h1 { font-size: 2.5rem; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); } /* Tamanho ajustado */
        .produto-imagem-container { width: 100%; height: 200px; overflow: hidden; background-color: #f0f0f0; display: flex; align-items: center; justify-content: center; cursor: pointer; } /* Altura ajustada */
        .produto-imagem { max-width: 100%; max-height: 100%; object-fit: contain; }
        .carrinho-item-img { width: 60px; height: 60px; object-fit: cover; margin-right: 10px; } /* Ajuste para mobile */
        #cart-count { font-size: 0.7rem; vertical-align: top; } /* Ajuste para mobile */
        .toast-container { z-index: 1100 !important; } 
        .modal { z-index: 1055 !important; } 
        .modal-backdrop { z-index: 1050 !important; }
        .modal-pix-body img { max-width: 200px; display: block; margin: 10px auto; border: 1px solid #ddd; padding: 8px; background-color: white; } /* Ajuste para mobile */
        .modal-pix-body .pix-code { word-break: break-all; background-color: #f0f0f0; padding: 8px; border-radius: 5px; font-family: monospace; font-size: 0.8em; margin-top:8px; } /* Ajuste para mobile */
        #imageModal .modal-dialog { max-width: 90vw; } /* Ajuste para mobile */
        #imageModal .modal-body img { max-width: 100%; max-height: 80vh; display: block; margin: auto; }
        #imageModal .modal-content { background-color: rgba(0,0,0,0.8); border: none; }
        #imageModal .modal-header { border-bottom: none; }
        #imageModal .btn-close { filter: invert(1) grayscale(100%) brightness(200%); }
        #confirmacaoPagamentoModal .modal-body p { margin-bottom: 0.5rem; font-size: 0.9rem; } /* Ajuste para mobile */
        #confirmacaoPagamentoModal .modal-body p.lead-message { font-size: 1rem; font-weight: 500; margin-bottom: 1rem;} /* Ajuste para mobile */

        /* Small devices (landscape phones, 576px and up) */
        @media (min-width: 576px) {
            .navbar-brand img.logo { max-height: 40px; margin-right: 10px; }
            .navbar-brand span { font-size: 1.5rem; }
            .nav-link { font-size: 1rem; }
            #cart-count { font-size: 0.75rem; }
            .hero-section { padding: 4rem 0; }
            .hero-section h1 { font-size: 2.8rem; }
            .produto-imagem-container { height: 220px; }
            .carrinho-item-img { width: 80px; height: 80px; margin-right: 15px; }
            .modal-pix-body img { max-width: 250px; padding: 10px;}
            .modal-pix-body .pix-code { padding: 10px; font-size: 0.9em; margin-top:10px; }
            #confirmacaoPagamentoModal .modal-body p { font-size: 0.95rem; }
            #confirmacaoPagamentoModal .modal-body p.lead-message { font-size: 1.1rem; }
        }
        /* Medium devices (tablets, 768px and up) */
        @media (min-width: 768px) {
             .hero-section { padding: 5rem 0; }
             .hero-section h1 { font-size: 3rem; }
             .section-title { font-size: 2rem; }
             .card-title { font-size: 1.25rem; }
        }
        .pedido-card { margin-bottom: 1.5rem; }
        .pedido-card .card-header { background-color: #e9ecef; }
        .pedido-card .list-group-item img { width: 50px; height: 50px; object-fit: cover; margin-right: 10px; border-radius: .25rem;}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm sticky-top">
        <div class="container">
            <a class="navbar-brand d-flex align-items-center" href="{{ url_inicio }}">
                <img src="{{ logo_url }}" alt="Logo {{ nome_empresa }}" class="logo">
                <span>{{ nome_empresa }}</span>
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"><span class="navbar-toggler-icon"></span></button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link {{ nav_inicio_active }}" href="{{ url_inicio }}">Início</a></li>
                    <li class="nav-item"><a class="nav-link {{ nav_produtos_active }}" href="{{ url_produtos }}">Produtos</a></li>
                    <li class="nav-item"><a class="nav-link {{ nav_pedidos_active }}" href="{{ url_pedidos }}"><i class="fas fa-receipt"></i> Meus Pedidos</a></li>
                    <li class="nav-item"><a class="nav-link {{ nav_carrinho_active }}" href="{{ url_carrinho }}"><i class="fas fa-shopping-cart"></i> Carrinho <span class="badge bg-success rounded-pill" id="cart-count">0</span></a></li>
                </ul>
            </div>
        </div>
    </nav>
    <div class="toast-container position-fixed top-0 end-0 p-3">
      <div id="feedbackToast" class="toast" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="5000">
        <div class="toast-header" id="toastHeader"> 
          <strong class="me-auto" id="toastTitle"><i class="fas fa-check-circle"></i> Sucesso!</strong>
          <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body" id="toastMessage">Operação realizada com sucesso.</div>
      </div>
    </div>
    <div class="modal fade" id="imageModal" tabindex="-1" aria-labelledby="imageModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered"> <div class="modal-content"> <div class="modal-header"> <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button> </div> <div class="modal-body text-center"> <img src="" id="modalImageSrc" alt="Imagem do Produto Ampliada"> </div> </div> </div>
    </div>
    <div class="modal fade" id="pixModal" tabindex="-1" aria-labelledby="pixModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered"> <div class="modal-content"> <div class="modal-header"> <h5 class="modal-title" id="pixModalLabel">Pagamento via PIX</h5> <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button> </div> <div class="modal-body modal-pix-body text-center"> <p>Escaneie o QR Code abaixo com o app do seu banco ou copie o código PIX.</p> <img id="pixQrCodeImg" src="" alt="QR Code PIX"> <p class="mt-2"><strong>Valor: R$ <span id="pixValor"></span></strong></p> <div class="input-group my-3"> <input type="text" id="pixCopiaECola" class="form-control" value="" readonly> <button class="btn btn-outline-secondary" type="button" id="btnCopiarPix"><i class="fas fa-copy"></i> Copiar</button> </div> <small class="text-muted">Após efetuar o pagamento, clique em "Já Paguei" para prosseguir (confirmação manual).</small> </div> <div class="modal-footer"> <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button> <button type="button" class="btn btn-success" id="btnConfirmarPixManual">Já Paguei</button> </div> </div> </div>
    </div>
    <div class="modal fade" id="confirmacaoPagamentoModal" tabindex="-1" aria-labelledby="confirmacaoModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered"> <div class="modal-content"> 
        <div class="modal-header bg-success text-white"> 
            <h5 class="modal-title" id="confirmacaoModalLabel"><i class="fas fa-check-circle"></i> Pagamento Confirmado!</h5> 
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button> 
        </div> 
        <div class="modal-body text-center"> 
            <i class="fas fa-gift fa-3x text-success my-3"></i>
            <p class="lead-message" id="confirmacaoValorCompra"></p>
            <p id="confirmacaoMensagemPrincipal"></p>
          
            <p><strong>Muito obrigado pela confiança em nosso trabalho.</strong></p>
            <small class="text-muted mt-2 d-block" id="confirmacaoMensagemAdicional"></small>
        </div> 
        <div class="modal-footer"> 
            <a href="{{ url_inicio }}" class="btn btn-primary">Voltar para Início</a> 
        </div> 
      </div> </div>
    </div>
    <div class="modal fade" id="boletoModal" tabindex="-1" aria-labelledby="boletoModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered"> <div class="modal-content"> <div class="modal-header"> <h5 class="modal-title" id="boletoModalLabel">Gerar Boleto Bancário</h5> <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button> </div> <div class="modal-body"> <p>Para gerar o boleto e enviá-lo para seu e-mail, por favor, informe seu nome e e-mail abaixo.</p> <div class="mb-3"> <label for="boletoNomeCliente" class="form-label">Nome Completo <span class="text-danger">*</span></label> <input type="text" class="form-control" id="boletoNomeCliente" placeholder="Seu Nome Completo" required> </div> <div class="mb-3"> <label for="boletoEmailCliente" class="form-label">E-mail <span class="text-danger">*</span></label> <input type="email" class="form-control" id="boletoEmailCliente" placeholder="seuemail@exemplo.com" required> </div> <p class="mt-2"><strong>Valor do Boleto: R$ <span id="boletoValor"></span></strong></p> <small class="text-muted">O boleto simulado será enviado para o e-mail informado.</small> </div> <div class="modal-footer"> <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button> <button type="button" class="btn btn-success" id="btnGerarEnviarBoleto">Gerar e Enviar Boleto</button> </div> </div> </div>
    </div>
    <div class="modal fade" id="cartaoModal" tabindex="-1" aria-labelledby="cartaoModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered"> <div class="modal-content"> <div class="modal-header"> <h5 class="modal-title" id="cartaoModalLabel">Pagamento com Cartão (Simulado)</h5> <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button> </div> <div class="modal-body"> <p>Esta é uma simulação de pagamento com cartão. Nenhum dado real será processado.</p> <div class="mb-3"> <label for="cartaoNumero" class="form-label">Número do Cartão</label> <input type="text" class="form-control" id="cartaoNumero" placeholder="0000 0000 0000 0000"> </div> <div class="row"> <div class="col-md-7 mb-3"> <label for="cartaoValidade" class="form-label">Validade (MM/AA)</label> <input type="text" class="form-control" id="cartaoValidade" placeholder="MM/AA"> </div> <div class="col-md-5 mb-3"> <label for="cartaoCVV" class="form-label">CVV</label> <input type="text" class="form-control" id="cartaoCVV" placeholder="000"> </div> </div> <p class="mt-2"><strong>Valor: R$ <span id="cartaoValor"></span></strong></p> </div> <div class="modal-footer"> <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button> <button type="button" class="btn btn-success" id="btnConfirmarCartaoSimulado">Pagar com Cartão (Simulado)</button> </div> </div> </div>
    </div>
    <main class="container mt-4 mb-5 flex-grow-1"> {{ content | safe }} </main>
    <footer class="footer text-center"> <div class="container"> <p>© {{ current_year }} {{ nome_empresa }}. Todos os direitos reservados.</p> </div> </footer>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const feedbackToastEl = document.getElementById('feedbackToast');
        const feedbackToast = feedbackToastEl ? new bootstrap.Toast(feedbackToastEl) : null;
        const imageModalEl = document.getElementById('imageModal');
        const imageModalInstance = imageModalEl ? new bootstrap.Modal(imageModalEl) : null; 
        const modalImageElement = document.getElementById('modalImageSrc');
        
        window.openImageModal = function(imageUrl) { 
            if (imageModalInstance && modalImageElement) { 
                modalImageElement.src = imageUrl; 
                imageModalInstance.show(); 
            }
        }
        
        function showToast(message, title = 'Sucesso!', type = 'success') {
            if (feedbackToast) {
                const toastHeader = document.getElementById('toastHeader'); 
                const toastTitleEl = document.getElementById('toastTitle'); 
                const toastMessageEl = document.getElementById('toastMessage'); 
                const toastButtonClose = toastHeader.querySelector('.btn-close');
                
                toastTitleEl.innerHTML = title; 
                toastMessageEl.textContent = message;
                toastHeader.classList.remove('bg-success', 'bg-danger', 'bg-warning', 'bg-info', 'text-white', 'text-dark'); 
                toastButtonClose.classList.remove('btn-close-white');

                if (type === 'success') { 
                    toastHeader.classList.add('bg-success', 'text-white'); 
                    toastButtonClose.classList.add('btn-close-white'); 
                    toastTitleEl.innerHTML = '<i class="fas fa-check-circle me-2"></i>' + title; 
                } else if (type === 'error') { 
                    toastHeader.classList.add('bg-danger', 'text-white'); 
                    toastButtonClose.classList.add('btn-close-white'); 
                    toastTitleEl.innerHTML = '<i class="fas fa-exclamation-circle me-2"></i>' + title; 
                } else if (type === 'warning') { 
                    toastHeader.classList.add('bg-warning', 'text-dark'); 
                    toastTitleEl.innerHTML = '<i class="fas fa-exclamation-triangle me-2"></i>' + title; 
                } else { 
                    toastHeader.classList.add('bg-info', 'text-white'); 
                    toastButtonClose.classList.add('btn-close-white'); 
                    toastTitleEl.innerHTML = '<i class="fas fa-info-circle me-2"></i>' + title; 
                }
                feedbackToast.show();
            } else { 
                alert( (type.toUpperCase() + ": " + title + "\\n" + message).replace(/<[^>]*>?/gm, '') ); 
            }
        }

        document.addEventListener('DOMContentLoaded', () => {
            let cart = JSON.parse(localStorage.getItem('zelarPlusCart')) || [];
            let pedidos = JSON.parse(localStorage.getItem('zelarPlusPedidos')) || [];


            function updateCartCount() {
                const cartCountElement = document.getElementById('cart-count');
                if (cartCountElement) {
                    const totalItems = cart.reduce((sum, item) => sum + item.quantidade, 0);
                    cartCountElement.textContent = totalItems;
                }
            }

            function saveCart() {
                localStorage.setItem('zelarPlusCart', JSON.stringify(cart));
                updateCartCount();
            }
            
            window.saveOrder = function(items, total) {
                const newOrder = {
                    id: 'ZLR-' + new Date().getTime() + '-' + Math.random().toString(36).substr(2, 5).toUpperCase(),
                    data: new Date().toISOString(),
                    itens: JSON.parse(JSON.stringify(items)), // Deep copy
                    total: total,
                    status: "Processando" // Status inicial simulado
                };
                pedidos.unshift(newOrder); // Adiciona no início para o mais recente aparecer primeiro
                localStorage.setItem('zelarPlusPedidos', JSON.stringify(pedidos));
            }


            window.addToCart = function(productId, productName, productPrice, productImage) {
                const existingProductIndex = cart.findIndex(item => item.id === productId);
                if (existingProductIndex > -1) {
                    cart[existingProductIndex].quantidade++;
                } else {
                    cart.push({ id: productId, nome: productName, preco: parseFloat(productPrice), imagem: productImage, quantidade: 1 });
                }
                saveCart();
                showToast(productName + ' adicionado ao carrinho!', 'Carrinho Atualizado', 'success');
                if (typeof renderCartPage === 'function' && (window.location.pathname.endsWith('/carrinho') || window.location.pathname.endsWith('/carrinho/'))) {
                    renderCartPage();
                }
                if (typeof renderCheckoutSummary === 'function' && (window.location.pathname.endsWith('/checkout') || window.location.pathname.endsWith('/checkout/'))) {
                    renderCheckoutSummary();
                }
            };

            window.removeFromCart = function(productId) {
                const productIndex = cart.findIndex(item => item.id === productId);
                if (productIndex > -1) {
                    if (cart[productIndex].quantidade > 1) {
                        cart[productIndex].quantidade--;
                    } else {
                        cart.splice(productIndex, 1);
                    }
                    saveCart();
                    showToast('Produto removido do carrinho.', 'Carrinho Atualizado', 'info');
                    if (typeof renderCartPage === 'function' && (window.location.pathname.endsWith('/carrinho') || window.location.pathname.endsWith('/carrinho/'))) {
                        renderCartPage();
                    }
                    if (typeof renderCheckoutSummary === 'function' && (window.location.pathname.endsWith('/checkout') || window.location.pathname.endsWith('/checkout/'))) {
                        renderCheckoutSummary();
                    }
                }
            };

            window.clearCart = function() {
                cart.length = 0; 
                saveCart(); 
                showToast('Carrinho esvaziado!', 'Carrinho Limpo', 'warning');
                
                if (typeof renderCartPage === 'function' && (window.location.pathname.endsWith('/carrinho') || window.location.pathname.endsWith('/carrinho/'))) {
                    renderCartPage();
                }
                if (typeof renderCheckoutSummary === 'function' && (window.location.pathname.endsWith('/checkout') || window.location.pathname.endsWith('/checkout/'))) {
                    renderCheckoutSummary();
                }
            };
            
            window.getCartItems = function() {
                return cart; 
            };

            window.getPedidos = function() {
                return pedidos;
            }
            
            updateCartCount(); 
        });
    </script>
    {{ extra_js | safe }}
</body>
</html>
"""

HTML_INDEX_CONTENT = """
    <div class="hero-section mb-5"> <div class="container"> <h1>Bem-vindo à {{ nome_empresa }}!</h1> <p class="lead">Sua jornada para uma vida mais saudável começa aqui.</p> <a href="{{ url_for('produtos_page') }}" class="btn btn-success btn-lg mt-3">Conheça Nossos Produtos</a> </div> </div>
    <div class="container"> <section id="missao" class="my-5 text-center"> <h2 class="section-title"><i class="fas fa-bullseye"></i> Nossa Missão</h2> <p class="lead">{{ missao }}</p> </section> <hr class="my-5"> <section id="visao" class="my-5 text-center"> <h2 class="section-title"><i class="fas fa-eye"></i> Nossa Visão</h2> <p class="lead">{{ visao }}</p> </section> <hr class="my-5"> <section id="destaques" class="my-5"> <h2 class="section-title text-center"><i class="fas fa-star"></i> Produtos em Destaque</h2> <div class="row"> {% for produto in produtos_destaque %} <div class="col-lg-4 col-md-6 mb-4"> <div class="card h-100"> <div class="produto-imagem-container" onclick="openImageModal('{{ url_for('static', filename='images/' + produto.imagem) }}')"> <img src="{{ url_for('static', filename='images/' + produto.imagem) }}" class="produto-imagem" alt="{{ produto.nome }}"> </div> <div class="card-body d-flex flex-column"> <h5 class="card-title">{{ produto.nome }}</h5> <p class="card-text flex-grow-1">{{ produto.descricao | truncate(80) }}</p> <p class="card-text fs-5 fw-bold">R$ {{ "%.2f"|format(produto.preco|float) }}</p> <button class="btn btn-primary mt-auto" onclick="addToCart({{ produto.id }}, '{{ produto.nome | escapejs }}', {{ produto.preco }}, '{{ produto.imagem | escapejs }}')"> <i class="fas fa-cart-plus"></i> Adicionar </button> </div> </div> </div> {% endfor %} </div> <div class="text-center mt-4"> <a href="{{ url_for('produtos_page') }}" class="btn btn-outline-primary btn-lg">Ver Todos os Produtos</a> </div> </section> </div>
"""

HTML_PRODUTOS_CONTENT = """
    <h1 class="mb-4 section-title text-center">Nossos Produtos</h1> <div class="row row-cols-1 row-cols-sm-2 row-cols-md-2 row-cols-lg-3 g-4"> {% for produto in produtos %} <div class="col"> <div class="card h-100"> <div class="produto-imagem-container" onclick="openImageModal('{{ url_for('static', filename='images/' + produto.imagem) }}')"> <img src="{{ url_for('static', filename='images/' + produto.imagem) }}" class="produto-imagem" alt="{{ produto.nome }}"> </div> <div class="card-body d-flex flex-column"> <h5 class="card-title">{{ produto.nome }}</h5> <p class="card-text text-muted small flex-grow-1">{{ produto.descricao }}</p> <p class="card-text fs-4 fw-bold mt-2">R$ {{ "%.2f"|format(produto.preco|float) }}</p> <button class="btn btn-primary mt-auto" onclick="addToCart({{ produto.id }}, '{{ produto.nome | escapejs }}', {{ produto.preco }}, '{{ produto.imagem | escapejs }}')"> <i class="fas fa-cart-plus"></i> Adicionar </button> </div> </div> </div> {% endfor %} </div>
"""

HTML_CARRINHO_CONTENT = """
    <h1 class="mb-4 section-title text-center">Seu Carrinho de Compras</h1> <div class="card"> <div class="card-body"> <div id="empty-cart-message" class="text-center py-5" style="display: none;"> <h4>Seu carrinho está vazio.</h4> <a href="{{ url_for('produtos_page') }}" class="btn btn-primary mt-3"><i class="fas fa-store"></i> Ver Produtos</a> </div> <div class="list-group mb-3" id="cart-items-container"> </div> <div id="cart-actions" style="display: none;"> <div class="d-flex justify-content-between align-items-center mt-3 pt-3 border-top flex-wrap"> <h4 class="mb-2 mb-md-0">Total: R$ <span id="cart-total">0.00</span></h4> <a href="{{ url_for('checkout_page') }}" class="btn btn-success btn-lg" id="btnFinalizarCompra"> <i class="fas fa-credit-card"></i> Finalizar Compra </a> </div> <div class="text-end mt-3"> <button class="btn btn-outline-danger" onclick="clearCart()"><i class="fas fa-times-circle"></i> Esvaziar Carrinho</button> </div> </div> </div> </div>
"""
HTML_CARRINHO_JS = """
<script>
    function renderCartPage() {
        const cartItems = getCartItems(); 
        const cartContainer = document.getElementById('cart-items-container'); 
        const cartTotalElement = document.getElementById('cart-total'); 
        const emptyCartMessage = document.getElementById('empty-cart-message'); 
        const cartActions = document.getElementById('cart-actions'); 
        const btnFinalizar = document.getElementById('btnFinalizarCompra');

        if(!cartContainer || !cartTotalElement || !emptyCartMessage || !cartActions || !btnFinalizar) { 
            return; 
        }
        cartContainer.innerHTML = ''; 
        let total = 0;

        if (cartItems.length === 0) { 
            emptyCartMessage.style.display = 'block'; 
            cartActions.style.display = 'none'; 
            btnFinalizar.classList.add('disabled'); 
            cartTotalElement.textContent = '0,00';
            return; 
        }
        
        emptyCartMessage.style.display = 'none'; 
        cartActions.style.display = 'block'; 
        btnFinalizar.classList.remove('disabled'); 
        
        cartItems.forEach(item => {
            const itemTotal = item.preco * item.quantidade; 
            total += itemTotal;
            const imagePath = item.imagem.startsWith('http') || item.imagem.startsWith('data:') ? item.imagem : `{{ url_for('static', filename='images/') }}${item.imagem}`;
            const safeItemName = item.nome.replace(/'/g, "\\\\'"); 
            const safeItemImage = item.imagem.replace(/'/g, "\\\\'");
            const itemElement = `
                <div class="list-group-item d-flex justify-content-between align-items-center flex-wrap">
                    <div class="d-flex align-items-center mb-2 mb-md-0 flex-grow-1"> 
                        <img src="${imagePath}" alt="${item.nome}" class="carrinho-item-img rounded"> 
                        <div> 
                            <h6 class="my-0">${item.nome}</h6> 
                            <small class="text-muted">Preço Un.: R$ ${item.preco.toFixed(2).replace('.', ',')}   |   Qtd: ${item.quantidade}</small> 
                        </div> 
                    </div>
                    <div class="text-end ms-md-3 mt-2 mt-md-0"> 
                        <span class="text-muted fw-bold fs-6 me-2">R$ ${itemTotal.toFixed(2).replace('.', ',')}</span> 
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="addToCart(${item.id}, '${safeItemName}', ${item.preco}, '${safeItemImage}')" title="Adicionar mais um"><i class="fas fa-plus"></i></button> 
                        <button class="btn btn-sm btn-outline-secondary" onclick="removeFromCart(${item.id})" title="Remover um"><i class="fas fa-minus"></i></button> 
                    </div>
                </div>`;
            cartContainer.innerHTML += itemElement;
        });
        if(cartTotalElement) cartTotalElement.textContent = total.toFixed(2).replace('.', ',');
    }

    if (window.location.pathname.endsWith('/carrinho') || window.location.pathname.endsWith('/carrinho/')) { 
        document.addEventListener('DOMContentLoaded', renderCartPage); 
    }
</script>
"""

HTML_CHECKOUT_CONTENT = """
    <h1 class="mb-4 section-title text-center">Finalizar Compra</h1> <div class="row"> <div class="col-md-7"> <div class="card mb-4"> <div class="card-header"><h4>Resumo do Pedido</h4></div> <div class="card-body"> <ul class="list-group list-group-flush mb-3" id="order-summary-items"></ul> <li class="list-group-item d-flex justify-content-between"> <span>Total (BRL)</span> <strong>R$ <span id="order-summary-total">0.00</span></strong> </li> </div> </div> </div> <div class="col-md-5"> <div class="card"> <div class="card-header"><h4>Formas de Pagamento</h4></div> <div class="card-body payment-options"> <p>Selecione uma forma de pagamento:</p> <div class="d-grid gap-2"> <button class="btn btn-outline-primary btn-lg w-100 mb-2" onclick="handlePaymentSelection('credito')"><i class="fas fa-credit-card"></i> Cartão de Crédito</button> <button class="btn btn-outline-primary btn-lg w-100 mb-2" onclick="handlePaymentSelection('debito')"><i class="far fa-credit-card"></i> Cartão de Débito</button> <button class="btn btn-outline-primary btn-lg w-100 mb-2" onclick="handlePaymentSelection('boleto')"><i class="fas fa-barcode"></i> Boleto Bancário</button> <button class="btn btn-outline-primary btn-lg w-100" onclick="handlePaymentSelection('pix')"><i class="fab fa-pix"></i> PIX</button> </div> </div> </div> </div> </div>
"""

# MODIFICADO: Adiciona saveOrder() na confirmação de pagamento
HTML_CHECKOUT_JS = r"""
<script>
    let currentPaymentTotal = 0; 
    var pixModalInstance, confirmacaoModalInstance, boletoModalInstance, cartaoModalInstance;

    document.addEventListener('DOMContentLoaded', () => {
        const pixModalEl = document.getElementById('pixModal');
        pixModalInstance = pixModalEl ? new bootstrap.Modal(pixModalEl) : null;
        
        const confirmacaoModalEl = document.getElementById('confirmacaoPagamentoModal');
        confirmacaoModalInstance = confirmacaoModalEl ? new bootstrap.Modal(confirmacaoModalEl) : null;
        
        const boletoModalEl = document.getElementById('boletoModal');
        boletoModalInstance = boletoModalEl ? new bootstrap.Modal(boletoModalEl) : null;
        
        const cartaoModalEl = document.getElementById('cartaoModal');
        cartaoModalInstance = cartaoModalEl ? new bootstrap.Modal(cartaoModalEl) : null;

        if (window.location.pathname.endsWith('/checkout') || window.location.pathname.endsWith('/checkout/')) {
            renderCheckoutSummary();
        }

        const btnCopiarPix = document.getElementById('btnCopiarPix');
        if(btnCopiarPix) {
            btnCopiarPix.addEventListener('click', function() {
                const pixCodeInput = document.getElementById('pixCopiaECola'); 
                pixCodeInput.select(); 
                pixCodeInput.setSelectionRange(0, 99999); 
                try {
                    navigator.clipboard.writeText(pixCodeInput.value)
                        .then(() => { 
                            this.innerHTML = '<i class="fas fa-check"></i> Copiado!'; 
                            showToast('Código PIX copiado!', 'Sucesso', 'success'); 
                            setTimeout(() => { this.innerHTML = '<i class="fas fa-copy"></i> Copiar'; }, 2000); 
                        })
                        .catch(err => { 
                            legacyCopyPix(this, pixCodeInput); 
                        });
                } catch (err) { 
                    legacyCopyPix(this, pixCodeInput);
                }
            });
        }
        function legacyCopyPix(buttonElement, inputElement) {
            try { 
                document.execCommand('copy'); 
                buttonElement.innerHTML = '<i class="fas fa-check"></i> Copiado!'; 
                showToast('Código PIX copiado!', 'Sucesso', 'success'); 
                setTimeout(() => { buttonElement.innerHTML = '<i class="fas fa-copy"></i> Copiar'; }, 2000); 
            } catch (e) { 
                showToast('Erro ao copiar o código PIX. Por favor, copie manualmente.', 'Erro ao Copiar', 'error'); 
            }
        }

        const btnConfirmarPixManual = document.getElementById('btnConfirmarPixManual');
        if(btnConfirmarPixManual) { 
            btnConfirmarPixManual.addEventListener('click', function() { 
                if (pixModalInstance) pixModalInstance.hide(); 
                if(typeof saveOrder === 'function') saveOrder(getCartItems(), currentPaymentTotal);
                showConfirmationModal("Pagamento PIX registrado. Seu pedido será processado após confirmação manual.", currentPaymentTotal); 
                if(typeof clearCart === 'function') clearCart(); 
            });
        }

        const btnConfirmarCartaoSimulado = document.getElementById('btnConfirmarCartaoSimulado');
        if(btnConfirmarCartaoSimulado) {
            btnConfirmarCartaoSimulado.addEventListener('click', function() {
                const numero = document.getElementById('cartaoNumero').value; 
                const validade = document.getElementById('cartaoValidade').value; 
                const cvv = document.getElementById('cartaoCVV').value;
                if (!numero || !validade || !cvv ) { showToast("Por favor, preencha todos os dados do cartão (simulados).", "Dados Incompletos", "warning"); return; }
                if (!/^[0-9]{13,19}$/.test(numero.replace(/\s/g, ''))) { showToast("Número de cartão inválido (simulado).", "Dados Inválidos", "warning"); return; }
                if (!/^(0[1-9]|1[0-2])\/?([0-9]{2})$/.test(validade)) { showToast("Validade do cartão inválida (MM/AA).", "Dados Inválidos", "warning"); return; }
                if (!/^[0-9]{3,4}$/.test(cvv)) { showToast("CVV do cartão inválido (simulado).", "Dados Inválidos", "warning"); return; }
                if (cartaoModalInstance) cartaoModalInstance.hide(); 
                if(typeof saveOrder === 'function') saveOrder(getCartItems(), currentPaymentTotal);
                showConfirmationModal("Pagamento com cartão confirmado (simulação).", currentPaymentTotal); 
                if(typeof clearCart === 'function') clearCart();
            });
        }
        
        const btnGerarEnviarBoleto = document.getElementById('btnGerarEnviarBoleto');
        if(btnGerarEnviarBoleto) {
            btnGerarEnviarBoleto.addEventListener('click', function() {
                const nomeCliente = document.getElementById('boletoNomeCliente').value.trim(); 
                const emailCliente = document.getElementById('boletoEmailCliente').value.trim();
                if (!nomeCliente) { showToast('Por favor, preencha seu nome completo.', 'Atenção!', 'warning'); document.getElementById('boletoNomeCliente').focus(); return; }
                if (!emailCliente) { showToast('Por favor, preencha seu e-mail.', 'Atenção!', 'warning'); document.getElementById('boletoEmailCliente').focus(); return; }
                if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailCliente)) { showToast('Por favor, insira um e-mail válido.', 'E-mail Inválido', 'warning'); document.getElementById('boletoEmailCliente').focus(); return; }
                
                this.disabled = true; 
                this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Enviando...';
                
                fetch('/api/enviar_boleto', { 
                    method: 'POST', 
                    headers: { 'Content-Type': 'application/json' }, 
                    body: JSON.stringify({ valor: currentPaymentTotal, nome_cliente: nomeCliente, email_cliente: emailCliente }) 
                })
                .then(response => response.json()).then(data => {
                    if (data.success) { 
                        if (boletoModalInstance) boletoModalInstance.hide(); 
                        if(typeof saveOrder === 'function') saveOrder(getCartItems(), currentPaymentTotal);
                        showConfirmationModal(`Boleto enviado para ${emailCliente}. Verifique sua caixa de entrada (e spam).`, currentPaymentTotal); 
                        if(typeof clearCart === 'function') clearCart();
                    } else { 
                        showToast(data.message || 'Erro ao gerar ou enviar o boleto.', 'Erro Boleto', 'error'); 
                    }
                }).catch(error => { 
                    showToast('Erro de comunicação ao enviar boleto. Tente novamente.', 'Erro de Rede', 'error'); 
                })
                .finally(() => { 
                    const btn = document.getElementById('btnGerarEnviarBoleto'); 
                    if (btn){ btn.disabled = false; btn.innerHTML = 'Gerar e Enviar Boleto';} 
                });
            });
        }
    }); 

    window.handlePaymentSelection = function(method) { 
        const totalPedidoStr = document.getElementById('order-summary-total').textContent.replace(',', '.'); 
        currentPaymentTotal = parseFloat(totalPedidoStr);
        
        if (isNaN(currentPaymentTotal) || currentPaymentTotal <= 0) { 
            showToast("Não há itens no carrinho ou valor inválido para pagamento.", "Atenção!", "warning"); 
            return; 
        }

        if (method === 'pix') {
            if (pixModalInstance) {
                document.getElementById('pixValor').textContent = currentPaymentTotal.toFixed(2).replace('.', ',');
                fetch(`/api/gerar_pix_qrcode?valor=${currentPaymentTotal}`)
                    .then(response => response.json()).then(data => {
                        if(data.qr_code_img_base64 && data.pix_copia_cola) { 
                            document.getElementById('pixQrCodeImg').src = data.qr_code_img_base64; 
                            document.getElementById('pixCopiaECola').value = data.pix_copia_cola; 
                            pixModalInstance.show(); 
                        } else { 
                            showToast(data.error || "Erro ao gerar QR Code PIX. Verifique se a chave PIX está configurada no servidor.", "Erro PIX", "error"); 
                        }
                    }).catch(error => { 
                        showToast("Erro de comunicação ao gerar PIX. Tente novamente.", "Erro de Rede", "error"); 
                    });
            }
        } else if (method === 'boleto') {
            if (boletoModalInstance) { 
                document.getElementById('boletoValor').textContent = currentPaymentTotal.toFixed(2).replace('.', ','); 
                document.getElementById('boletoNomeCliente').value = ''; 
                document.getElementById('boletoEmailCliente').value = ''; 
                boletoModalInstance.show(); 
            }
        } else if (method === 'credito' || method === 'debito') {
             if (cartaoModalInstance) { 
                document.getElementById('cartaoValor').textContent = currentPaymentTotal.toFixed(2).replace('.', ','); 
                document.getElementById('cartaoModalLabel').textContent = `Pagamento com Cartão de ${method === 'credito' ? 'Crédito' : 'Débito'} (Simulado)`; 
                document.getElementById('cartaoNumero').value = ''; 
                document.getElementById('cartaoValidade').value = ''; 
                document.getElementById('cartaoCVV').value = ''; 
                cartaoModalInstance.show(); 
            }
        }
    }

    function showConfirmationModal(additionalMsgText = "", valorCompra = 0.0) { 
        if (confirmacaoModalInstance) { 
            const valorCompraEl = document.getElementById('confirmacaoValorCompra');
            const msgPrincipalEl = document.getElementById('confirmacaoMensagemPrincipal');
            const additionalMsgEl = document.getElementById('confirmacaoMensagemAdicional');
            
            if(valorCompraEl) {
                 valorCompraEl.textContent = `Agradecemos sinceramente pela sua compra no valor de R$ ${valorCompra.toFixed(2).replace('.', ',')}.`;
            }
            if(msgPrincipalEl) {
                msgPrincipalEl.textContent = "Ficamos felizes em poder atender você e informamos que seu pedido será cuidadosamente preparado e entregue no prazo estimado de até 7 dias úteis.";
            }
            if(additionalMsgEl) {
                additionalMsgEl.textContent = additionalMsgText; 
            }
            confirmacaoModalInstance.show(); 
        } else { 
            const mensagemCompleta = `Agradecemos sinceramente pela sua compra no valor de R$ ${valorCompra.toFixed(2).replace('.', ',')}.\\n` +
                                     "Ficamos felizes em poder atender você e informamos que seu pedido será cuidadosamente preparado e entregue no prazo estimado de até 7 dias úteis.\\n" +
                                     "Caso tenha qualquer dúvida ou precise de ajuda, estamos à disposição para atendê-lo(a).\\n" +
                                     "Esperamos que aproveite muito seu produto e que volte sempre para conferir nossas novidades!\\n" +
                                     "Muito obrigado pela confiança em nosso trabalho.\\n" + 
                                     (additionalMsgText ? "\\n(" + additionalMsgText + ")" : "") +
                                     "\\nObrigado por comprar na {{ nome_empresa }}!";
            alert(mensagemCompleta); 
            window.location.href = "{{ url_for('index') }}"; 
        }
    }
    
    window.renderCheckoutSummary = function() {
        const cartItems = typeof getCartItems === 'function' ? getCartItems() : [];
        const summaryContainer = document.getElementById('order-summary-items');
        const summaryTotalElement = document.getElementById('order-summary-total');
        const paymentButtons = document.querySelectorAll('.payment-options button'); 

        if (!summaryContainer || !summaryTotalElement) { 
            return; 
        }
        
        summaryContainer.innerHTML = ''; 
        let total = 0;

        if (cartItems.length > 0) {
            cartItems.forEach(item => {
                const itemTotal = item.preco * item.quantidade; 
                total += itemTotal;
                const imagePath = item.imagem.startsWith('http') || item.imagem.startsWith('data:') ? item.imagem : `{{ url_for('static', filename='images/') }}${item.imagem}`;
                const li = document.createElement('li'); 
                li.className = 'list-group-item d-flex justify-content-between lh-sm';
                li.innerHTML = `
                    <div class="d-flex align-items-center"> 
                        <img src="${imagePath}" alt="${item.nome}" class="me-2" style="width:50px; height:50px; object-fit:cover; border-radius: .25rem;"> 
                        <div> 
                            <h6 class="my-0">${item.nome}</h6> 
                            <small class="text-muted">Qtd: ${item.quantidade} x R$ ${item.preco.toFixed(2).replace('.',',')}</small> 
                        </div> 
                    </div> 
                    <span class="text-muted">R$ ${itemTotal.toFixed(2).replace('.',',')}</span>`;
                summaryContainer.appendChild(li);
            });
            if (paymentButtons) paymentButtons.forEach(btn => btn.disabled = false); 
        } else {
            summaryContainer.innerHTML = '<li class="list-group-item text-center py-3"><p class="mb-0">Seu carrinho está vazio. <a href="{{ url_for('produtos_page') }}">Adicionar produtos</a></p></li>';
            if (paymentButtons) paymentButtons.forEach(btn => btn.disabled = true); 
        }
        
        summaryTotalElement.textContent = total.toFixed(2).replace('.',',');
        currentPaymentTotal = total; 
    }
</script>
"""

# NOVO: HTML para a página "Meus Pedidos"
HTML_MEUS_PEDIDOS_CONTENT = """
    <h1 class="mb-4 section-title text-center"><i class="fas fa-receipt"></i> Meus Pedidos</h1>
    <div id="pedidos-container">
        <!-- Pedidos serão renderizados aqui pelo JavaScript -->
    </div>
    <div id="sem-pedidos-mensagem" class="text-center py-5" style="display: none;">
        <h4>Você ainda não fez nenhum pedido.</h4>
        <a href="{{ url_for('produtos_page') }}" class="btn btn-primary mt-3"><i class="fas fa-store"></i> Ver Produtos</a>
    </div>
"""

# NOVO: JavaScript para a página "Meus Pedidos"
HTML_MEUS_PEDIDOS_JS = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    const pedidosContainer = document.getElementById('pedidos-container');
    const semPedidosMensagem = document.getElementById('sem-pedidos-mensagem');
    const pedidos = window.getPedidos ? window.getPedidos() : [];

    if (!pedidosContainer || !semPedidosMensagem) return;

    if (pedidos.length === 0) {
        semPedidosMensagem.style.display = 'block';
        pedidosContainer.style.display = 'none';
    } else {
        semPedidosMensagem.style.display = 'none';
        pedidosContainer.style.display = 'block';
        pedidos.forEach(pedido => {
            const dataPedido = new Date(pedido.data);
            const dataFormatada = `${dataPedido.toLocaleDateString('pt-BR')} às ${dataPedido.toLocaleTimeString('pt-BR', {hour: '2-digit', minute:'2-digit'})}`;
            
            let itensHtml = '<ul class="list-group list-group-flush">';
            pedido.itens.forEach(item => {
                const imagePath = item.imagem.startsWith('http') || item.imagem.startsWith('data:') ? item.imagem : `{{ url_for('static', filename='images/') }}${item.imagem}`;
                itensHtml += `
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <div class="d-flex align-items-center">
                            <img src="${imagePath}" alt="${item.nome}">
                            <span>${item.nome} (Qtd: ${item.quantidade})</span>
                        </div>
                        <span>R$ ${(item.preco * item.quantidade).toFixed(2).replace('.', ',')}</span>
                    </li>`;
            });
            itensHtml += '</ul>';

            const pedidoCard = `
                <div class="card pedido-card shadow-sm">
                    <div class="card-header">
                        <div class="d-flex justify-content-between align-items-center flex-wrap">
                            <h5 class="mb-1 mb-md-0">Pedido #${pedido.id}</h5>
                            <span class="badge bg-info text-dark">${pedido.status || 'Processando'}</span>
                        </div>
                    </div>
                    <div class="card-body">
                        <p class="card-text"><strong>Data:</strong> ${dataFormatada}</p>
                        <p class="card-text"><strong>Itens do Pedido:</strong></p>
                        ${itensHtml}
                    </div>
                    <div class="card-footer text-end">
                        <strong>Total do Pedido: R$ ${pedido.total.toFixed(2).replace('.', ',')}</strong>
                    </div>
                </div>
            `;
            pedidosContainer.innerHTML += pedidoCard;
        });
    }
});
</script>
"""


def render_page_content(page_content_template_string, page_title, extra_js_string="", **kwargs_for_content):
    if 'produtos_destaque' not in kwargs_for_content and page_title == "Início":
        kwargs_for_content['produtos_destaque'] = PRODUTOS[:6]

    js_context = kwargs_for_content.copy()
    js_context['nome_empresa'] = EMPRESA_NOME


    rendered_content = render_template_string(page_content_template_string, **kwargs_for_content)
    rendered_extra_js = Markup(render_template_string(extra_js_string, **js_context)) if extra_js_string else ""


    base_args = {
        "nome_empresa": EMPRESA_NOME, 
        "logo_url": url_for('static', filename=f'images/{EMPRESA_LOGO_FILENAME}'),
        "page_title": page_title, 
        "current_year": datetime.now().year,
        "content": Markup(rendered_content),
        "extra_js": rendered_extra_js, 
        "nav_inicio_active": "active" if page_title == "Início" else "",
        "nav_produtos_active": "active" if page_title == "Produtos" else "",
        "nav_pedidos_active": "active" if page_title == "Meus Pedidos" else "", # NOVO
        "nav_carrinho_active": "active" if page_title == "Carrinho" or page_title == "Finalizar Compra" else "",
        "url_inicio": url_for('index'),
        "url_produtos": url_for('produtos_page'),
        "url_pedidos": url_for('meus_pedidos_page'), # NOVO
        "url_carrinho": url_for('carrinho_page')
    }
    return render_template_string(HTML_BASE_STRUCTURE, **base_args)


@app.route('/')
def index():
    return render_page_content(HTML_INDEX_CONTENT, "Início", missao=EMPRESA_MISSAO, visao=EMPRESA_VISAO, nome_empresa=EMPRESA_NOME)

@app.route('/produtos')
def produtos_page():
    return render_page_content(HTML_PRODUTOS_CONTENT, "Produtos", produtos=PRODUTOS)

# NOVA ROTA E FUNÇÃO
@app.route('/meus_pedidos')
def meus_pedidos_page():
    return render_page_content(HTML_MEUS_PEDIDOS_CONTENT, "Meus Pedidos", extra_js_string=HTML_MEUS_PEDIDOS_JS)

@app.route('/carrinho')
def carrinho_page():
    return render_page_content(HTML_CARRINHO_CONTENT, "Carrinho", extra_js_string=HTML_CARRINHO_JS)

@app.route('/checkout')
def checkout_page():
    return render_page_content(HTML_CHECKOUT_CONTENT, "Finalizar Compra", extra_js_string=HTML_CHECKOUT_JS, nome_empresa=EMPRESA_NOME)


@app.route('/api/gerar_pix_qrcode')
def api_gerar_pix_qrcode():
    valor_str = request.args.get('valor', '0.00')
    try: valor = float(valor_str)
    except ValueError: valor = 0.00

    if CHAVE_PIX_REAL == "SUA_CHAVE_PIX_REAL_AQUI" or not CHAVE_PIX_REAL:
        return jsonify({"error": "Chave PIX para pagamento não configurada no servidor."}), 500

    txid_unico = "ZLR" + str(uuid.uuid4()).replace('-', '')[:22]
    pix_copia_cola = gerar_pix_payload(
        chave_pix=CHAVE_PIX_REAL, 
        valor=valor, 
        nome_beneficiario=EMPRESA_NOME, 
        cidade_beneficiario=EMPRESA_CIDADE, 
        txid=txid_unico
    )

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=3)
    qr.add_data(pix_copia_cola)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO(); img.save(buffered, format="PNG"); img_str = base64.b64encode(buffered.getvalue()).decode()
    return jsonify({"qr_code_img_base64": f"data:image/png;base64,{img_str}", "pix_copia_cola": pix_copia_cola})

@app.route('/api/enviar_boleto', methods=['POST'])
def api_enviar_boleto():
    data = request.get_json(); 
    valor = data.get('valor'); 
    nome_cliente = data.get('nome_cliente'); 
    email_cliente = data.get('email_cliente')
    
    if not all([isinstance(valor, (int, float)), nome_cliente, email_cliente]): 
        return jsonify({"success": False, "message": "Dados incompletos ou inválidos. Nome, e-mail e valor numérico são obrigatórios."}), 400
    
    try: 
        valor = float(valor)
        if valor <= 0: raise ValueError("Valor deve ser positivo")
    except (ValueError, TypeError): 
        return jsonify({"success": False, "message": "Valor do boleto inválido."}), 400
        
    num_pedido_simulado = str(uuid.uuid4().int)[:8]
    try:
        boleto_pdf_bytes = gerar_boleto_pdf_simulado(valor, nome_cliente, email_cliente, EMPRESA_NOME, num_pedido_simulado)
        sender_email = app.config['MAIL_DEFAULT_SENDER']
        if '<' not in sender_email: 
            sender_email = f'"{EMPRESA_NOME}" <{sender_email}>'

        msg = Message(f"Seu Boleto Simulado - Pedido {num_pedido_simulado} - {EMPRESA_NOME}", 
                      sender=sender_email, 
                      recipients=[email_cliente])
        msg.body = f"Olá {nome_cliente},\n\nSegue em anexo o boleto simulado para sua compra de R$ {valor:.2f} na {EMPRESA_NOME}.\n\nNúmero do Pedido: {num_pedido_simulado}\n\nLembre-se que este é um boleto de demonstração e não possui valor real.\n\nAtenciosamente,\nEquipe {EMPRESA_NOME}"
        msg.attach(f"boleto_{num_pedido_simulado}.pdf", "application/pdf", boleto_pdf_bytes.read())
        mail.send(msg)
        return jsonify({"success": True, "message": "Boleto enviado com sucesso para seu e-mail!"})
    except Exception as e: 
        print(f"Erro ao enviar boleto: {e}")
        error_message = "Ocorreu um erro ao processar o envio do boleto. "
        if "authentication" in str(e).lower() or "authorization" in str(e).lower():
             error_message += "Verifique as configurações de e-mail do servidor. "
        error_message += "Tente novamente mais tarde."
        return jsonify({"success": False, "message": error_message}), 500


@app.route('/api/produtos/<int:produto_id>')
def get_produto(produto_id):
    produto = next((p for p in PRODUTOS if p["id"] == produto_id), None)
    if produto: return jsonify(produto)
    return jsonify({"erro": "Produto não encontrado"}), 404

if __name__ == '__main__':
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    images_dir = os.path.join(static_dir, 'images')
    if not os.path.exists(static_dir): os.makedirs(static_dir); print(f"Pasta criada: {static_dir}")
    if not os.path.exists(images_dir): os.makedirs(images_dir); print(f"Pasta criada: {images_dir}")

    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', f'"Zelar +" <{app.config["MAIL_USERNAME"]}>')

    print("\n--- INSTRUÇÕES IMPORTANTES PARA FUNCIONAMENTO ---")
    print(f"1. Certifique-se de que a pasta '{images_dir}' existe DENTRO de uma pasta 'static' na raiz do seu projeto.")
    print(f"2. COPIE as imagens dos seus produtos (ex: {EMPRESA_LOGO_FILENAME}, imagem1.jpeg ...) para '{images_dir}'.")
    print("3. Verifique os nomes dos arquivos de imagem em `PRODUTOS` (maiúsculas/minúsculas importam!).")
    print("4. Para o envio de e-mail do BOLETO:")
    print("   - Instale: pip install Flask Flask-Mail fpdf2 qrcode Pillow Unidecode markupsafe")
    print(f"  - Configure `MAIL_USERNAME` e `MAIL_PASSWORD` (ou use variáveis de ambiente).")
    print(f"  - Para Gmail, use uma 'Senha de App' se tiver 2FA ativado.")
    print("\n5. PARA PAGAMENTO PIX REAL:")
    print(f"   - Edite a variável `CHAVE_PIX_REAL` (ex: seu e-mail, CPF, CNPJ, chave aleatória) e `EMPRESA_CIDADE` neste script.")
    print("     Lembre-se: A confirmação do pagamento no sistema ainda é manual (botão 'Já Paguei').")
    print("\n6. 'MEUS PEDIDOS' é uma simulação e usa o localStorage do navegador.")
    print("--------------------------------------------------\n")

    if CHAVE_PIX_REAL == "SUA_CHAVE_PIX_REAL_AQUI" or not CHAVE_PIX_REAL : print("ATENÇÃO: `CHAVE_PIX_REAL` não configurada ou inválida. O QR Code PIX não funcionará com uma conta real.\n")
    if app.config.get('MAIL_USERNAME') == 'SEU_EMAIL_GMAIL@gmail.com' or not app.config.get('MAIL_USERNAME'): print("ATENÇÃO: Credenciais de e-mail não configuradas. O envio de boletos PODE NÃO FUNCIONAR.\n")

    app.run(host='0.0.0.0', port=5000, debug=True)