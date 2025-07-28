const form = document.getElementById("chat-form");
const input = document.getElementById("user-input");
const box = document.getElementById("chat-box");
const box_top = document.querySelector("#top");
const typingIndicator = document.getElementById("typing-indicator");

function scroll() {
    box.scrollTop = box.scrollHeight;
}


form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = input.value;
    if (!message.trim()) return;

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