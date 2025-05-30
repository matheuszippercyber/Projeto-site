// js/script.js

// --- Variáveis Globais e Configurações ---
let cart = JSON.parse(localStorage.getItem('zelarPlusCart')) || [];
let pedidos = JSON.parse(localStorage.getItem('zelarPlusPedidos')) || [];
let currentPaymentTotal = 0;

// Instâncias dos Modais (serão inicializadas no DOMContentLoaded)
var pixModalInstance, confirmacaoModalInstance, boletoModalInstance, cartaoModalInstance, imageModalInstance;

// --- Funções Utilitárias ---
function escapeJS(value) {
    if (typeof value !== 'string') return value;
    return value.replace(/'/g, "\\'").replace(/"/g, '\\"');
}

function showToast(message, title = 'Sucesso!', type = 'success') {
    const feedbackToastEl = document.getElementById('feedbackToast');
    if (!feedbackToastEl) {
        alert(`${type.toUpperCase()}: ${title}\n${message}`);
        return;
    }
    const feedbackToast = bootstrap.Toast.getInstance(feedbackToastEl) || new bootstrap.Toast(feedbackToastEl);

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
        toastTitleEl.innerHTML = `<i class="fas fa-check-circle me-2"></i> ${title}`;
    } else if (type === 'error') {
        toastHeader.classList.add('bg-danger', 'text-white');
        toastButtonClose.classList.add('btn-close-white');
        toastTitleEl.innerHTML = `<i class="fas fa-exclamation-circle me-2"></i> ${title}`;
    } else if (type === 'warning') {
        toastHeader.classList.add('bg-warning', 'text-dark');
        toastTitleEl.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i> ${title}`;
    } else {
        toastHeader.classList.add('bg-info', 'text-white');
        toastButtonClose.classList.add('btn-close-white');
        toastTitleEl.innerHTML = `<i class="fas fa-info-circle me-2"></i> ${title}`;
    }
    feedbackToast.show();
}

function openImageModal(imageUrl) {
    const modalImageElement = document.getElementById('modalImageSrc');
    if (imageModalInstance && modalImageElement) {
        modalImageElement.src = imageUrl;
        imageModalInstance.show();
    }
}

// --- Funções do Carrinho ---
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

function addToCart(productId, productName, productPrice, productImage) {
    const existingProductIndex = cart.findIndex(item => item.id === productId);
    if (existingProductIndex > -1) {
        cart[existingProductIndex].quantidade++;
    } else {
        cart.push({ id: productId, nome: productName, preco: parseFloat(productPrice), imagem: productImage, quantidade: 1 });
    }
    saveCart();
    showToast(`${productName} adicionado ao carrinho!`, 'Carrinho Atualizado', 'success');

    // Atualiza a página do carrinho ou checkout se estiver nelas
    if (document.getElementById('cart-items-container')) renderCartPage();
    if (document.getElementById('order-summary-items')) renderCheckoutSummary();
}

function removeFromCart(productId) {
    const productIndex = cart.findIndex(item => item.id === productId);
    if (productIndex > -1) {
        if (cart[productIndex].quantidade > 1) {
            cart[productIndex].quantidade--;
        } else {
            cart.splice(productIndex, 1);
        }
        saveCart();
        showToast('Produto removido do carrinho.', 'Carrinho Atualizado', 'info');
        if (document.getElementById('cart-items-container')) renderCartPage();
        if (document.getElementById('order-summary-items')) renderCheckoutSummary();
    }
}

function clearCart() {
    cart = [];
    saveCart();
    showToast('Carrinho esvaziado!', 'Carrinho Limpo', 'warning');
    if (document.getElementById('cart-items-container')) renderCartPage();
    if (document.getElementById('order-summary-items')) renderCheckoutSummary();
     // Se estiver na página de checkout e o carrinho for esvaziado, redirecionar ou desabilitar opções
    if (document.getElementById('order-summary-items') && cart.length === 0) {
        const paymentButtons = document.querySelectorAll('.payment-options button');
        if (paymentButtons) paymentButtons.forEach(btn => btn.disabled = true);
         // Opcional: redirecionar para a página de produtos ou carrinho
        // window.location.href = 'carrinho.html';
    }
}

// --- Funções de Pedidos ---
function saveOrder(items, total) {
    const newOrder = {
        id: 'ZLR-' + new Date().getTime() + '-' + Math.random().toString(36).substr(2, 5).toUpperCase(),
        data: new Date().toISOString(),
        itens: JSON.parse(JSON.stringify(items)), // Deep copy
        total: total,
        status: "Processando"
    };
    pedidos.unshift(newOrder);
    localStorage.setItem('zelarPlusPedidos', JSON.stringify(pedidos));
}

// --- Funções de Renderização de Páginas Específicas ---
function renderHomePage() {
    // Injeta informações da empresa na página inicial
    const empresaNomeElements = document.querySelectorAll('.empresa-nome-placeholder');
    empresaNomeElements.forEach(el => el.textContent = EMPRESA_NOME);
    
    const missaoEl = document.getElementById('missao-empresa');
    if (missaoEl) missaoEl.textContent = EMPRESA_MISSAO;
    
    const visaoEl = document.getElementById('visao-empresa');
    if (visaoEl) visaoEl.textContent = EMPRESA_VISAO;

    // Renderiza produtos em destaque
    const destaquesContainer = document.getElementById('produtos-destaque-container');
    if (destaquesContainer) {
        destaquesContainer.innerHTML = ''; // Limpa antes de adicionar
        const produtosDestaque = PRODUTOS.slice(0, 6); // Pega os 6 primeiros
        produtosDestaque.forEach(produto => {
            const cardHtml = `
                <div class="col-lg-4 col-md-6 mb-4">
                    <div class="card h-100">
                        <div class="produto-imagem-container" onclick="openImageModal('images/${produto.imagem}')">
                            <img src="images/${produto.imagem}" class="produto-imagem" alt="${escapeJS(produto.nome)}">
                        </div>
                        <div class="card-body d-flex flex-column">
                            <h5 class="card-title">${escapeJS(produto.nome)}</h5>
                            <p class="card-text flex-grow-1">${escapeJS(produto.descricao.substring(0, 80))}${produto.descricao.length > 80 ? '...' : ''}</p>
                            <p class="card-text fs-5 fw-bold">R$ ${produto.preco.toFixed(2).replace('.', ',')}</p>
                            <button class="btn btn-primary mt-auto" onclick="addToCart(${produto.id}, '${escapeJS(produto.nome)}', ${produto.preco}, '${escapeJS(produto.imagem)}')">
                                <i class="fas fa-cart-plus"></i> Adicionar
                            </button>
                        </div>
                    </div>
                </div>`;
            destaquesContainer.innerHTML += cardHtml;
        });
    }
}

function renderProductsPage() {
    const produtosContainer = document.getElementById('todos-produtos-container');
    if (produtosContainer) {
        produtosContainer.innerHTML = '';
        PRODUTOS.forEach(produto => {
            const cardHtml = `
                <div class="col">
                    <div class="card h-100">
                        <div class="produto-imagem-container" onclick="openImageModal('images/${produto.imagem}')">
                            <img src="images/${produto.imagem}" class="produto-imagem" alt="${escapeJS(produto.nome)}">
                        </div>
                        <div class="card-body d-flex flex-column">
                            <h5 class="card-title">${escapeJS(produto.nome)}</h5>
                            <p class="card-text text-muted small flex-grow-1">${escapeJS(produto.descricao)}</p>
                            <p class="card-text fs-4 fw-bold mt-2">R$ ${produto.preco.toFixed(2).replace('.', ',')}</p>
                            <button class="btn btn-primary mt-auto" onclick="addToCart(${produto.id}, '${escapeJS(produto.nome)}', ${produto.preco}, '${escapeJS(produto.imagem)}')">
                                <i class="fas fa-cart-plus"></i> Adicionar
                            </button>
                        </div>
                    </div>
                </div>`;
            produtosContainer.innerHTML += cardHtml;
        });
    }
}

function renderCartPage() {
    const cartContainer = document.getElementById('cart-items-container');
    const cartTotalElement = document.getElementById('cart-total');
    const emptyCartMessage = document.getElementById('empty-cart-message');
    const cartActions = document.getElementById('cart-actions');
    const btnFinalizar = document.getElementById('btnFinalizarCompra');

    if (!cartContainer || !cartTotalElement || !emptyCartMessage || !cartActions || !btnFinalizar) return;

    cartContainer.innerHTML = '';
    let total = 0;

    if (cart.length === 0) {
        emptyCartMessage.style.display = 'block';
        cartActions.style.display = 'none';
        btnFinalizar.classList.add('disabled');
        cartTotalElement.textContent = '0,00';
    } else {
        emptyCartMessage.style.display = 'none';
        cartActions.style.display = 'block';
        btnFinalizar.classList.remove('disabled');
        cart.forEach(item => {
            const itemTotal = item.preco * item.quantidade;
            total += itemTotal;
            const imagePath = `images/${item.imagem}`;
            const itemElement = `
                <div class="list-group-item d-flex justify-content-between align-items-center flex-wrap">
                    <div class="d-flex align-items-center mb-2 mb-md-0 flex-grow-1">
                        <img src="${imagePath}" alt="${escapeJS(item.nome)}" class="carrinho-item-img rounded">
                        <div>
                            <h6 class="my-0">${escapeJS(item.nome)}</h6>
                            <small class="text-muted">Preço Un.: R$ ${item.preco.toFixed(2).replace('.', ',')}   |   Qtd: ${item.quantidade}</small>
                        </div>
                    </div>
                    <div class="text-end ms-md-3 mt-2 mt-md-0">
                        <span class="text-muted fw-bold fs-6 me-2">R$ ${itemTotal.toFixed(2).replace('.', ',')}</span>
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="addToCart(${item.id}, '${escapeJS(item.nome)}', ${item.preco}, '${escapeJS(item.imagem)}')" title="Adicionar mais um"><i class="fas fa-plus"></i></button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="removeFromCart(${item.id})" title="Remover um"><i class="fas fa-minus"></i></button>
                    </div>
                </div>`;
            cartContainer.innerHTML += itemElement;
        });
        cartTotalElement.textContent = total.toFixed(2).replace('.', ',');
    }
}

function renderCheckoutSummary() {
    const summaryContainer = document.getElementById('order-summary-items');
    const summaryTotalElement = document.getElementById('order-summary-total');
    const paymentButtons = document.querySelectorAll('.payment-options button');

    if (!summaryContainer || !summaryTotalElement) return;

    summaryContainer.innerHTML = '';
    let total = 0;

    if (cart.length > 0) {
        cart.forEach(item => {
            const itemTotal = item.preco * item.quantidade;
            total += itemTotal;
            const imagePath = `images/${item.imagem}`;
            const li = document.createElement('li');
            li.className = 'list-group-item d-flex justify-content-between lh-sm';
            li.innerHTML = `
                <div class="d-flex align-items-center">
                    <img src="${imagePath}" alt="${escapeJS(item.nome)}" class="me-2" style="width:50px; height:50px; object-fit:cover; border-radius: .25rem;">
                    <div>
                        <h6 class="my-0">${escapeJS(item.nome)}</h6>
                        <small class="text-muted">Qtd: ${item.quantidade} x R$ ${item.preco.toFixed(2).replace('.', ',')}</small>
                    </div>
                </div>
                <span class="text-muted">R$ ${itemTotal.toFixed(2).replace('.', ',')}</span>`;
            summaryContainer.appendChild(li);
        });
        if (paymentButtons) paymentButtons.forEach(btn => btn.disabled = false);
    } else {
        summaryContainer.innerHTML = '<li class="list-group-item text-center py-3"><p class="mb-0">Seu carrinho está vazio. <a href="produtos.html">Adicionar produtos</a></p></li>';
        if (paymentButtons) paymentButtons.forEach(btn => btn.disabled = true);
    }
    summaryTotalElement.textContent = total.toFixed(2).replace('.', ',');
    currentPaymentTotal = total;
}

function renderPedidosPage() {
    const pedidosContainer = document.getElementById('pedidos-container');
    const semPedidosMensagem = document.getElementById('sem-pedidos-mensagem');

    if (!pedidosContainer || !semPedidosMensagem) return;

    if (pedidos.length === 0) {
        semPedidosMensagem.style.display = 'block';
        pedidosContainer.style.display = 'none';
    } else {
        semPedidosMensagem.style.display = 'none';
        pedidosContainer.style.display = 'block';
        pedidosContainer.innerHTML = '';
        pedidos.forEach(pedido => {
            const dataPedido = new Date(pedido.data);
            const dataFormatada = `${dataPedido.toLocaleDateString('pt-BR')} às ${dataPedido.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}`;
            let itensHtml = '<ul class="list-group list-group-flush">';
            pedido.itens.forEach(item => {
                const imagePath = `images/${item.imagem}`;
                itensHtml += `
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <div class="d-flex align-items-center">
                            <img src="${imagePath}" alt="${escapeJS(item.nome)}">
                            <span>${escapeJS(item.nome)} (Qtd: ${item.quantidade})</span>
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
                </div>`;
            pedidosContainer.innerHTML += pedidoCard;
        });
    }
}

// --- Lógica de Pagamento (Simulada) ---
function handlePaymentSelection(method) {
    const totalPedidoStr = document.getElementById('order-summary-total')?.textContent.replace(',', '.') || '0';
    currentPaymentTotal = parseFloat(totalPedidoStr);

    if (isNaN(currentPaymentTotal) || currentPaymentTotal <= 0) {
        showToast("Não há itens no carrinho ou valor inválido para pagamento.", "Atenção!", "warning");
        return;
    }

    if (method === 'pix') {
        if (pixModalInstance) {
            document.getElementById('pixValor').textContent = currentPaymentTotal.toFixed(2).replace('.', ',');
            document.getElementById('pixQrCodeImg').src ='images/qr_code_pix_placeholder.jpeg';
            document.getElementById('pixCopiaECola').value = 'Aguardando Pagamento';
            pixModalInstance.show();
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

        if (valorCompraEl) valorCompraEl.textContent = `Agradecemos sinceramente pela sua compra no valor de R$ ${valorCompra.toFixed(2).replace('.', ',')}.`;
        if (msgPrincipalEl) msgPrincipalEl.textContent = "Ficamos felizes em poder atender você e informamos que seu pedido será cuidadosamente preparado e entregue no prazo estimado de até 7 dias úteis.";
        if (additionalMsgEl) additionalMsgEl.textContent = additionalMsgText;
        confirmacaoModalInstance.show();
    } else {
        alert(`Pagamento confirmado (simulação)! Valor: R$ ${valorCompra.toFixed(2)}\n${additionalMsgText}\nObrigado por comprar na ${EMPRESA_NOME}!`);
        window.location.href = "index.html";
    }
}


// --- Inicialização e Event Listeners ---
document.addEventListener('DOMContentLoaded', () => {
    // Inicializa instâncias de modais do Bootstrap
    const pixModalEl = document.getElementById('pixModal');
    if (pixModalEl) pixModalInstance = new bootstrap.Modal(pixModalEl);

    const confirmacaoModalEl = document.getElementById('confirmacaoPagamentoModal');
    if (confirmacaoModalEl) confirmacaoModalInstance = new bootstrap.Modal(confirmacaoModalEl);

    const boletoModalEl = document.getElementById('boletoModal');
    if (boletoModalEl) boletoModalInstance = new bootstrap.Modal(boletoModalEl);

    const cartaoModalEl = document.getElementById('cartaoModal');
    if (cartaoModalEl) cartaoModalInstance = new bootstrap.Modal(cartaoModalEl);

    const imageModalEl = document.getElementById('imageModal');
    if (imageModalEl) imageModalInstance = new bootstrap.Modal(imageModalEl);

    // Preenche dados globais da empresa (ex: nome no footer, navbar)
    const empresaNomeGlobalElements = document.querySelectorAll('.empresa-nome-global');
    empresaNomeGlobalElements.forEach(el => el.textContent = EMPRESA_NOME);
    const logoImg = document.getElementById('navbar-logo-img');
    if (logoImg) logoImg.src = `images/${EMPRESA_LOGO_FILENAME}`;
    const currentYearEl = document.getElementById('current-year');
    if(currentYearEl) currentYearEl.textContent = new Date().getFullYear();


    // Lógica de qual página está ativa para renderizar conteúdo específico
    const path = window.location.pathname.split("/").pop();

    if (path === 'index.html' || path === '') {
        renderHomePage();
    } else if (path === 'produtos.html') {
        renderProductsPage();
    } else if (path === 'carrinho.html') {
        renderCartPage();
    } else if (path === 'checkout.html') {
        renderCheckoutSummary();
    } else if (path === 'meus_pedidos.html') {
        renderPedidosPage();
    }
    
    updateCartCount(); // Atualiza contador do carrinho ao carregar qualquer página

    // Event Listeners para Modais de Pagamento
    const btnCopiarPix = document.getElementById('btnCopiarPix');
    if (btnCopiarPix) {
        btnCopiarPix.addEventListener('click', function() {
            const pixCodeInput = document.getElementById('pixCopiaECola');
            pixCodeInput.select();
            pixCodeInput.setSelectionRange(0, 99999); // Para mobile
            try {
                navigator.clipboard.writeText(pixCodeInput.value)
                    .then(() => {
                        this.innerHTML = '<i class="fas fa-check"></i> Copiado!';
                        showToast('Código PIX copiado!', 'Sucesso', 'success');
                        setTimeout(() => { this.innerHTML = '<i class="fas fa-copy"></i> Copiar'; }, 2000);
                    })
                    .catch(err => { // Fallback para document.execCommand
                        document.execCommand('copy');
                        this.innerHTML = '<i class="fas fa-check"></i> Copiado!';
                        showToast('Código PIX copiado! (fallback)', 'Sucesso', 'success');
                        setTimeout(() => { this.innerHTML = '<i class="fas fa-copy"></i> Copiar'; }, 2000);
                    });
            } catch (err) {
                showToast('Erro ao copiar. Por favor, copie manualmente.', 'Erro', 'error');
            }
        });
    }

    const btnConfirmarPixManual = document.getElementById('btnConfirmarPixManual');
    if (btnConfirmarPixManual) {
        btnConfirmarPixManual.addEventListener('click', function() {
            if (pixModalInstance) pixModalInstance.hide();
            saveOrder(cart, currentPaymentTotal);
            showConfirmationModal("Pagamento PIX registrado .", currentPaymentTotal);
            clearCart();
        });
    }

    const btnGerarEnviarBoleto = document.getElementById('btnGerarEnviarBoleto');
    if (btnGerarEnviarBoleto) {
        btnGerarEnviarBoleto.addEventListener('click', function() {
            const nomeCliente = document.getElementById('boletoNomeCliente').value.trim();
            const emailCliente = document.getElementById('boletoEmailCliente').value.trim();
            if (!nomeCliente || !emailCliente || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailCliente)) {
                showToast('Por favor, preencha nome e e-mail válidos.', 'Atenção!', 'warning'); return;
            }
            // SIMULAÇÃO: Não envia e-mail nem gera PDF
            if (boletoModalInstance) boletoModalInstance.hide();
            saveOrder(cart, currentPaymentTotal);
            showConfirmationModal(`Boleto "gerado" para ${emailCliente} .`, currentPaymentTotal);
            clearCart();
        });
    }

    const btnConfirmarCartaoSimulado = document.getElementById('btnConfirmarCartao');
    if (btnConfirmarCartaoSimulado) {
        btnConfirmarCartaoSimulado.addEventListener('click', function() {
            const numero = document.getElementById('cartaoNumero').value;
            const validade = document.getElementById('cartaoValidade').value;
            const cvv = document.getElementById('cartaoCVV').value;
            if (!numero || !validade || !cvv ) { showToast("Por favor, preencha todos os dados do cartão (simulados).", "Dados Incompletos", "warning"); return; }
            if (!/^[0-9]{13,19}$/.test(numero.replace(/\s/g, ''))) { showToast("Número de cartão inválido (simulado).", "Dados Inválidos", "warning"); return; }
            if (!/^(0[1-9]|1[0-2])\/?([0-9]{2})$/.test(validade)) { showToast("Validade do cartão inválida (MM/AA).", "Dados Inválidos", "warning"); return; }
            if (!/^[0-9]{3,4}$/.test(cvv)) { showToast("CVV do cartão inválido .", "Dados Inválidos", "warning"); return; }
            
            if (cartaoModalInstance) cartaoModalInstance.hide();
            saveOrder(cart, currentPaymentTotal);
            showConfirmationModal("Pagamento com cartão confirmado .", currentPaymentTotal);
            clearCart();
        });
    }

    // Highlight active nav link
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    const currentPath = window.location.pathname.substring(window.location.pathname.lastIndexOf("/") + 1);
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href').split("/").pop();
        if (linkPath === currentPath || (currentPath === '' && linkPath === 'index.html')) {
            link.classList.add('active-nav-link');
        } else {
            link.classList.remove('active-nav-link');
        }
    });
});