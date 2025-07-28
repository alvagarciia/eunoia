const form = document.getElementById("chat-form");
const input = document.getElementById("user-input");
const box = document.getElementById("chat-box");
const box_top = document.querySelector("#top");
const typingIndicator = document.getElementById("typing-indicator");

// Remove welcome message on first interaction
let isFirstMessage = true;

form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = input.value;
    if (!message.trim()) return;

    // Remove welcome message on first user input
    if (isFirstMessage) {
        const welcomeMsg = box.querySelector('.welcome-message');
        if (welcomeMsg) {
            welcomeMsg.style.animation = 'fadeOut 0.3s ease-out forwards';
            welcomeMsg.remove();
            // setTimeout(() => welcomeMsg.remove(), 300);
        }
        isFirstMessage = false;
    }

    // Add user message with bubble styling
    const userMessage = document.createElement('div');
    userMessage.className = 'user-message';
    userMessage.innerHTML = `
        <div class="message-bubble user-bubble">
            <div class="message-sender">You</div>
            ${message}
        </div>
    `;
    box_top.append(userMessage);
    input.value = "";

    // Show typing indicator
    setTimeout(() => typingIndicator.classList.remove('hidden'), 500);
    box.scrollTop = box.scrollHeight;

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message }),
        });

        const data = await res.json();
        
        // Hide typing indicator
        typingIndicator.classList.add('hidden');
        
        // Add assistant message with bubble styling
        const formattedReply = data.reply.replace(/\n/g, '<br>');
        const assistantMessage = document.createElement('div');
        assistantMessage.className = 'assistant-message';
        assistantMessage.innerHTML = `
            <div class="message-bubble assistant-bubble">
                <div class="message-sender">Noema</div>
                ${formattedReply}
            </div>
        `;
        box_top.append(assistantMessage);
        box.scrollTop = box.scrollHeight;
        
    } catch (error) {
        // Hide typing indicator on error
        typingIndicator.classList.add('hidden');
        
        const errorMessage = document.createElement('div');
        errorMessage.className = 'assistant-message';
        errorMessage.innerHTML = `
            <div class="message-bubble assistant-bubble">
                <div class="message-sender">Noema</div>
                I'm sorry, I'm having trouble responding right now. Please try again in a moment.
            </div>
        `;
        box_top.append(errorMessage);
        box.scrollTop = box.scrollHeight;
    }
});