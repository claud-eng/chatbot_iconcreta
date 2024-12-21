(function () {
    // Cargar estilos personalizados
    var customStylesLink = document.createElement('link');
    customStylesLink.rel = 'stylesheet';
    var currentUrl = window.location.href;
    var url = new URL(currentUrl);
    var domain = url.hostname;

    // Cargar archivo CSS dependiendo de la URL
    if (domain.includes('desarrollo.iconcreta.com')) {
        customStylesLink.href = '/static/css/widget.css';
    } else if (domain.includes('www.espacioandres.cl')) {
        customStylesLink.href = '/static/css/widget_lfl_inmo168.css';
    } else if (domain.includes('www.vimac.cl')) {
        customStylesLink.href = '/static/css/widget_vimac.css';
    } else if (domain.includes('www.ivmc.cl')) {
        customStylesLink.href = '/static/css/widget_vmc.css';
    } else if (domain.includes('desarrollos.want.cl')) {
        customStylesLink.href = '/static/css/widget_vmc.css';
    } else {
        customStylesLink.href = '/static/css/widget.css'; // Archivo CSS por defecto
    }

    document.head.appendChild(customStylesLink);

    var isChatWidgetInitialized = false; // Controla si el widget ya fue inicializado

    function initChatWidget() {
        if (isChatWidgetInitialized) return; // Evita inicializar el widget más de una vez
        isChatWidgetInitialized = true;

        // Crear contenedor principal del widget de chat
        var chatWidgetDiv = document.createElement('div');
        chatWidgetDiv.classList.add('chat-widget');
        document.body.appendChild(chatWidgetDiv);

        var domainTextMap = {
            'www.vimac.cl': 'Asistente Virtual Vimac',
            'vimac.cl': 'Asistente Virtual Vimac',
            'www.ivmc.cl': 'Asistente Virtual VMC',
            'ivmc.cl': 'Asistente Virtual VMC',
            'desarrollos.want.cl': 'Asistente Virtual VMC',
            'localhost': 'Asistente Virtual VMC',
            // Agregar más dominios y sus textos correspondientes según sea necesario
        };
    
        var mainText = domainTextMap[domain] || 'Asistente Virtual';
        var logoText = `
            <span class="main-text">${mainText}</span><br>
            <span class="small-text"><i>Desarrollado por</i> <a href="https://iconcreta.com/" target="_blank"><i>www.iconcreta.com</i></a></span>
        `;
    
        // Agregar el HTML interno del widget de chat
        chatWidgetDiv.innerHTML = `
            <div class="chat-header">
                <div class="chat-logo-text">
                    ${logoText}
                </div>
                <button class="minimize-chat-btn">-</button>
                <button class="toggle-chat-btn">Chat</button>
            </div>
            <div class="chat-container shadow-sm">
                <div id="chatBox" class="chat-content shadow-sm"></div>
                <div class="input-group">
                    <input type="text" id="messageInput" class="form-control" placeholder="Escribe tu mensaje aquí...">
                    <div class="input-group-append">
                        <button class="btn btn-primary" type="button">Enviar</button>
                    </div>
                </div>
            </div>
        `;

        var sendButton = chatWidgetDiv.querySelector('.input-group-append .btn');
        sendButton.addEventListener('click', function () {
            sendMessage();
        });

                // Definir las imágenes según el dominio
        var domainIconMap = {
            'www.vimac.cl': '/static/img/vimac_icon.png',
            'vimac.cl': '/static/img/vimac_icon.png',
            'www.ivmc.cl': '/static/img/vmc_icon.png',
            'ivmc.cl': '/static/img/vmc_icon.png',
            'desarrollos.want.cl': '/static/img/vmc_icon.png',
            'www.desarrollos.want.cl': '/static/img/vmc_icon.png',
            'localhost': '/static/img/alejandra_icon.png',
            // Agregar más dominios y sus respectivas imágenes según sea necesario
        };

        // Crear y agregar el botón de maximizar fuera del chatWidgetDiv
        var minimizedIcon = document.createElement('img');
        minimizedIcon.className = 'minimized-icon';
        minimizedIcon.src = domainIconMap[domain] || '/static/img/alejandra_icon.png'; // Imagen por defecto si no coincide con ningún dominio
        minimizedIcon.alt = 'Abrir Chatbot';
        minimizedIcon.onclick = function () { toggleChat(true); };
        minimizedIcon.style.display = 'none'; // Inicialmente oculto
        document.body.appendChild(minimizedIcon);

        // Crear y agregar la burbuja de mensaje
        var messageBubble = document.createElement('div');
        messageBubble.className = 'message-bubble';
        messageBubble.innerHTML = '¡Hola! ¿Necesitas ayuda para cotizar? <br> ¡Déjame ayudarte!';
        messageBubble.onclick = function () {
            toggleChat(true);
            minimizedIcon.style.display = 'none';
            messageBubble.style.display = 'none';
        };
        document.body.appendChild(messageBubble);

        var minimizeChatButton = chatWidgetDiv.querySelector('.minimize-chat-btn');
        var toggleChatButton = chatWidgetDiv.querySelector('.toggle-chat-btn');

        minimizeChatButton.addEventListener('click', function () {
            toggleChat(false); // Minimizar
        });
        toggleChatButton.addEventListener('click', function () {
            toggleChat(true); // Maximizar
        });

        // Mostrar la burbuja de mensaje solo la primera vez que se carga la página
        if (!getWithExpiry('chatBubbleShown')) {
            var bubbleTimeout = setTimeout(function () {
                messageBubble.style.display = 'none';
            }, 15000);
            messageBubble.style.display = 'block';
            setWithExpiry('chatBubbleShown', 'true', 2 * 24 * 60 * 60 * 1000); // Marcar que la burbuja fue mostrada
        } else {
            messageBubble.style.display = 'none';
        }

        // Cargar el estado guardado del chat
        var chatState = loadChatState();
        toggleChat(chatState === 'open'); // Llama directamente a la función con true o false según el estado guardado

        // Funciones para manipular el widget de chat
        function toggleChat(shouldOpen) {
            if (shouldOpen) {
                chatWidgetDiv.classList.add('open');
                chatWidgetDiv.classList.remove('minimized');
                minimizedIcon.style.display = 'none';
                messageBubble.style.display = 'none'; // Ocultar la burbuja al maximizar
                saveChatState(true); // Guardar el estado como abierto
                clearTimeout(bubbleTimeout); // Detener el timeout si se abre el chat
            } else {
                chatWidgetDiv.classList.remove('open');
                chatWidgetDiv.classList.add('minimized');
                minimizedIcon.style.display = 'block'; // Asegura que el botón de maximizar se muestre cuando el chat se minimiza
                saveChatState(false); // Guardar el estado como minimizado
            }
        }

        function sendMessage(messageToSend = null, optionText = null) {
            var messageInput = chatWidgetDiv.querySelector('#messageInput');
            var message = messageToSend || messageInput.value.trim();
            var displayMessage = optionText || message;

            if (message) {
                if (messageToSend !== 'inicio') {
                    appendMessage('user', displayMessage);
                }
                messageInput.value = '';
                messageInput.setAttribute('disabled', 'disabled');

                var chatSessionId = getWithExpiry('chatSessionId');
                if (!chatSessionId) {
                    chatSessionId = generateUniqueId();
                    setWithExpiry('chatSessionId', chatSessionId, 2 * 24 * 60 * 60 * 1000); // 2 días en milisegundos
                }

                var urlActual = window.location.href;

                fetch(`/chatbot/flujo_dptos_casas/?message=${encodeURIComponent(message)}&url=${encodeURIComponent(urlActual)}&chatSessionId=${chatSessionId}`, {
                    credentials: 'include'
                })
                .then(response => response.json())
                .then(data => {
                    appendMessage('bot', data.respuesta, data.respuesta.includes('href=') || data.respuesta.includes('<a '));
                    handleBotOptions(data.options, data.state); // Pasa el estado actual al manejar las opciones
                    if (debeHabilitarCampoDeEntrada(data.options)) {
                        messageInput.removeAttribute('disabled');
                    }
                    saveConversationState(); // Guardar el estado de la conversación
                })
                .catch(error => {
                    console.error('Error:', error);
                    messageInput.removeAttribute('disabled');
                });
            }
        }

        // Función para generar un ID único
        function generateUniqueId() {
            return Math.random().toString(36).substr(2, 9);
        }

        // Función para manejar las opciones del bot
        function handleBotOptions(options, state) {
            var chatBox = chatWidgetDiv.querySelector('#chatBox');
            removePreviousOptions(); // Eliminar las opciones anteriores
        
            // Obtener la URL actual para verificar el dominio
            var currentUrl = window.location.href;
            var parsedUrl = new URL(currentUrl);
            var currentDomain = parsedUrl.hostname;
        
            // Lista de dominios sin selección automática
            var dominiosSinSeleccionAutomatica = ['desarrollos.want.cl', 'ivmc.cl', 'localhost'];
        
            if (options && options.length > 0) {
                setWithExpiry('chatBotOptionsAvailable', 'true', 2 * 24 * 60 * 60 * 1000); // 2 días en milisegundos
        
                // Condición para determinar si aplicar la selección automática
                if (state === 'seleccionando_proyecto' && options.length === 1 && !dominiosSinSeleccionAutomatica.includes(currentDomain)) {
                    // Selección automática para flujo 'seleccionando_proyecto' con una sola opción
                    sendMessage(options[0].value, options[0].text, true);
                    return;
                }
        
                options.forEach(function (option) {
                    var optionButton = document.createElement('button');
                    optionButton.textContent = option.text;
                    optionButton.classList.add('option-button', 'btn', 'btn-primary', 'm-2');
                    optionButton.setAttribute('data-value', option.value);
                    optionButton.onclick = function () {
                        disableOptionButtons();
                        sendMessage(option.value, option.text);
                    };
                    chatBox.appendChild(optionButton);
                });
                chatBox.scrollTop = chatBox.scrollHeight;
                return;
            }
            removeItemWithExpiry('chatBotOptionsAvailable'); // No hay opciones disponibles
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        // Función para deshabilitar botones de opciones
        function disableOptionButtons() {
            var optionButtons = chatWidgetDiv.querySelectorAll('.option-button');
            optionButtons.forEach(function (button) {
                button.setAttribute('disabled', 'disabled');
            });
        }

        // Función para eliminar opciones anteriores
        function removePreviousOptions() {
            var chatBox = chatWidgetDiv.querySelector('#chatBox');
            var optionButtons = chatBox.querySelectorAll('.option-button');
            optionButtons.forEach(function (button) {
                chatBox.removeChild(button);
            });
        }

        // Función para añadir mensaje al chat
        function appendMessage(sender, message, isHtml = false) {
            var chatBox = chatWidgetDiv.querySelector('#chatBox');
            var messageDiv = document.createElement('div');
            messageDiv.classList.add('message');
        
            if (sender === 'user') {
                messageDiv.classList.add('user-message');
                message = 'Tú: ' + message;
            } else {
                messageDiv.classList.add('bot-message');
                message = 'Alejandra: ' + message;
            }
        
            if (isHtml) {
                messageDiv.innerHTML = message;
            } else {
                messageDiv.textContent = message;
            }
        
            chatBox.appendChild(messageDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        // Función para determinar si el campo de entrada debe estar habilitado
        function debeHabilitarCampoDeEntrada(options) {
            return options.length === 0;
        }

        // Funciones para guardar y cargar el estado de la conversación
        function saveConversationState() {
            var chatBox = chatWidgetDiv.querySelector('#chatBox');
            var messages = chatBox.innerHTML;
            setWithExpiry('chatConversationState', messages, 2 * 24 * 60 * 60 * 1000); // 2 días en milisegundos
            
            var chatOptions = [];
            chatWidgetDiv.querySelectorAll('.option-button').forEach(button => {
                chatOptions.push({ text: button.textContent, value: button.getAttribute('data-value') });
            });
            setWithExpiry('chatBotOptionsState', JSON.stringify(chatOptions), 2 * 24 * 60 * 60 * 1000); // 2 días en milisegundos
        }

        // Función para cargar el estado de la conversación
        function loadConversationState() {
            var chatBox = chatWidgetDiv.querySelector('#chatBox');
            var messages = getWithExpiry('chatConversationState');
            if (messages) {
                chatBox.innerHTML = messages;
                chatBox.scrollTop = chatBox.scrollHeight;
                
                var chatOptions = getWithExpiry('chatBotOptionsState');
                if (chatOptions) {
                    removePreviousOptions(); // Eliminar las opciones anteriores antes de restaurar
                    var options = JSON.parse(chatOptions);
                    options.forEach(option => {
                        var optionButton = document.createElement('button');
                        optionButton.textContent = option.text;
                        optionButton.classList.add('option-button', 'btn', 'btn-primary', 'm-2');
                        optionButton.setAttribute('data-value', option.value);
                        optionButton.onclick = function () {
                            disableOptionButtons();
                            sendMessage(option.value, option.text);
                        };
                        chatBox.appendChild(optionButton);
                    });
                    chatBox.scrollTop = chatBox.scrollHeight;
                    return true; // Indica que se ha cargado un estado de conversación
                }
            }
            return false; // No se encontró un estado de conversación anterior
        }

        // Función para guardar el estado del chatbot (minimizado o maximizado)
        function saveChatState(isOpen) {
            setWithExpiry('chatWidgetState', isOpen ? 'open' : 'minimized', 2 * 24 * 60 * 60 * 1000); // 2 días en milisegundos
        }

        // Función para cargar el estado del chatbot
        function loadChatState() {
            return getWithExpiry('chatWidgetState');
        }

        // Inicialización y eventos
        var input = chatWidgetDiv.querySelector('#messageInput');
        input.addEventListener('keypress', function (event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                sendMessage();
            }
        });

        if (!loadConversationState()) { // Cargar el estado de la conversación, si no hay, enviar el mensaje de inicio
            sendMessage('inicio');
        }

        // Restaurar el estado de las opciones al cargar
        if (getWithExpiry('chatBotOptionsAvailable') === 'true') {
            input.setAttribute('disabled', 'disabled'); // Deshabilitar el campo de entrada si hay opciones disponibles
        }
    }

    // Verificar si el DOM está completamente cargado
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initChatWidget);
    } else {
        initChatWidget();
    }

    // Funciones para manejar el almacenamiento con expiración
    function setWithExpiry(key, value, ttl) {
        const now = new Date();

        // item es un objeto que contiene el valor y la fecha de expiración
        const item = {
            value: value,
            expiry: now.getTime() + ttl,
        }
        localStorage.setItem(key, JSON.stringify(item));
    }

    // Función para obtener datos con expiración de localStorage
    function getWithExpiry(key) {
        const itemStr = localStorage.getItem(key);

        // Si el item no existe, devuelve null
        if (!itemStr) {
            return null;
        }

        const item = JSON.parse(itemStr);
        const now = new Date();

        // Compara la fecha de expiración con la fecha actual
        if (now.getTime() > item.expiry) {
            // Si el item ha expirado, elimínalo de localStorage
            localStorage.removeItem(key);
            return null;
        }
        return item.value;
    }

    // Función para eliminar datos de localStorage
    function removeItemWithExpiry(key) {
        localStorage.removeItem(key);
    }

})();

