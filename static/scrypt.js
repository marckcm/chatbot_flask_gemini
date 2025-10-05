document.addEventListener("DOMContentLoaded", function () {
AOS.init();
feather.replace();

const chatContainer = document.querySelector(".chatbot-container");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const quickReplyBtns = document.querySelectorAll(".quick-reply-btn");
const typingIndicator = document.getElementById("typing-indicator");

function addMessage(message, isUser) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("chatbot-message", "p-3", "self-start");
    if (isUser) {
    messageDiv.classList.add("user-message", "self-end");
    } else {
    messageDiv.classList.add("bot-message");
    }
    messageDiv.innerHTML = `<p>${message}</p>`;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showTypingIndicator(show) {
    typingIndicator.style.display = show ? "block" : "none";
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Função para enviar mensagem para o backend
async function botReply(message) {
    showTypingIndicator(true);

    try {
    // Enviar mensagem para o backend
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify({
        message: message,
        timestamp: new Date().toISOString()
        }),
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    // Verificar se a resposta tem o formato esperado
    if (data.response) {
        addMessage(data.response, false);
    } else {
        throw new Error('Resposta inválida do servidor');
    }

    } catch (error) {
    console.error("Erro ao comunicar com o servidor:", error);
    
    // Mensagem de fallback
    let errorMessage = "Desculpe, estou com dificuldades técnicas no momento. ";
    
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
        errorMessage += "Verifique sua conexão com a internet ou tente novamente mais tarde.";
    } else if (error.message.includes('HTTP error')) {
        errorMessage += "Nosso servidor está temporariamente indisponível. Tente novamente em alguns minutos.";
    } else {
        errorMessage += "Por favor, tente novamente ou entre em contato pelo telefone para atendimento imediato.";
    }
    
    addMessage(errorMessage, false);
    } finally {
    setTimeout(() => {
        showTypingIndicator(false);
    }, 1000);
    }
}

// Manipulador de clique do botão Enviar
sendBtn.addEventListener("click", function () {
    const message = userInput.value.trim();
    if (message) {
    addMessage(message, true);
    userInput.value = "";
    botReply(message);
    }
});

// Manipulador da tecla Enter
userInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
    sendBtn.click();
    }
});

// Botões de resposta rápida
quickReplyBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
    const message = this.textContent.trim();
    addMessage(message, true);
    botReply(message);
    });
});

// Mensagem inicial após carregamento
setTimeout(() => {
    addMessage(
    "Estou aqui para ajudar com qualquer dúvida que você tenha. Sinta-se à vontade para perguntar!",
    false
    );
}, 3000);
});
