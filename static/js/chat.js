const form = document.getElementById("chat-form");
const input = document.getElementById("user-input");
const box = document.getElementById("chat-box");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = input.value;
  if (!message.trim()) return;

  box.innerHTML += `<p><b>You:</b> ${message}</p>`;
  input.value = "";

  const res = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  const data = await res.json();
  box.innerHTML += `<p><b>Assistant:</b> ${data.reply}</p>`;
  box.scrollTop = box.scrollHeight;
});