const form = document.getElementById("chat-form");
const input = document.getElementById("user-input");
const box = document.getElementById("chat-box");
const box_top = document.querySelector("#top");
const typingIndicator = document.getElementById("typing-indicator");

function scroll() {
    box.scrollTop = box.scrollHeight;
}

// Auto-resize textarea functionality
function autoResizeTextarea() {
    // Reset height to calculate new height
    input.style.height = 'auto';
    
    // Calculate the new height
    const newHeight = Math.min(input.scrollHeight, 130); // Max height 130px (~4 lines)
    input.style.height = newHeight + 'px';
    
    // Add scrollable class if content exceeds max height
    if (input.scrollHeight > 130) {
        input.classList.add('scrollable');
    } else {
        input.classList.remove('scrollable');
    }
}

// Auto-resize on input
input.addEventListener('input', autoResizeTextarea);

// Handle Enter key (send on Enter, new line on Shift+Enter)
input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        form.dispatchEvent(new Event('submit'));
    }
});

// Reset textarea height after sending message
function resetTextarea() {
    input.style.height = 'auto';
    input.classList.remove('scrollable');
}

form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = input.value.trim();
    if (!message) return;

    // Add user message with bubble styling
    const userMessage = document.createElement('div');
    userMessage.className = 'user-message';
    userMessage.innerHTML = `
        <div class="message-bubble user-bubble">
            <div class="message-sender">You</div>
            ${message.replace(/\n/g, '<br>')}
        </div>
    `;
    box_top.append(userMessage);
    input.value = "";
    resetTextarea(); // Reset textarea height
    box.scrollTop = box.scrollHeight;

    // Show typing indicator
    setTimeout(() => typingIndicator.classList.remove('hidden'), 500);
    typingIndicator.classList.remove('hidden')
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
        box_top.append(assistantMessage)
        box.scrollTop = box.scrollHeight;
        
    } catch (error) {
        // Hide typing indicator on error
        setTimeout(() => typingIndicator.classList.add('hidden'), 500);
        
        const errorMessage = document.createElement('div');
        errorMessage.className = 'assistant-message';
        errorMessage.innerHTML = `
            <div class="message-bubble assistant-bubble">
                <div class="message-sender">Noema</div>
                I'm sorry, I'm having trouble responding right now. Please try again in a moment.
            </div>
        `;
        setTimeout(() => box_top.append(errorMessage), 500);
        setTimeout(() => scroll(), 500);
    }
});