const chat = document.getElementById("chat");
const form = document.getElementById("chat-form");
const questionInput = document.getElementById("question");
const sendBtn = document.getElementById("send-btn");

function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.textContent = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
  return div;
}

function formatDetails(data) {
  const followUps = Array.isArray(data.follow_up_questions) && data.follow_up_questions.length
    ? data.follow_up_questions.map((q, i) => `${i + 1}. ${q}`).join("\n")
    : "None";

  return [
    "",
    "Details:",
    `Confidence: ${data.confidence ?? "N/A"}`,
    `Reasoning: ${data.reasoning ?? "N/A"}`,
    `Follow-up Questions:\n${followUps}`,
    `Sources Needed: ${data.sources_needed ? "Yes" : "No"}`,
  ].join("\n");
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const rawInput = questionInput.value.trim();
  if (!rawInput) return;
  const questions = rawInput.split("\n").map((q) => q.trim()).filter(Boolean);

  addMessage("user", rawInput);
  questionInput.value = "";

  sendBtn.disabled = true;
  const botMsg = addMessage("bot", "Thinking...");

  try {
    if (questions.length > 1) {
      const batchResponse = await fetch("/api/ask-batch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ questions }),
      });

      if (!batchResponse.ok) {
        let errorText = "Batch request failed.";
        try {
          const data = await batchResponse.json();
          errorText = data.detail || errorText;
        } catch (_) {}
        botMsg.textContent = `Error: ${errorText}`;
        return;
      }

      const items = await batchResponse.json();
      const lines = items.map((item, idx) => {
        const answer = item.answer ?? "No answer";
        return `Q${idx + 1}: ${questions[idx]}\nA${idx + 1}: ${answer}${formatDetails(item)}\n`;
      });
      botMsg.textContent = lines.join("\n");
      return;
    }

    const question = questions[0];
    const streamResponse = await fetch("/api/ask-stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    if (!streamResponse.ok) {
      let errorText = "Request failed.";
      try {
        const data = await streamResponse.json();
        errorText = data.detail || errorText;
      } catch (_) {}
      botMsg.textContent = `Error: ${errorText}`;
      return;
    }

    const reader = streamResponse.body.getReader();
    const decoder = new TextDecoder();
    let answerText = "";

    botMsg.textContent = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      answerText += decoder.decode(value, { stream: true });
      botMsg.textContent = answerText;
      chat.scrollTop = chat.scrollHeight;
    }

    const detailsResponse = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    if (detailsResponse.ok) {
      const data = await detailsResponse.json();
      botMsg.textContent = (answerText || data.answer || "").trim() + formatDetails(data);
    }
  } catch (error) {
    botMsg.textContent = `Network error: ${error.message}`;
  } finally {
    sendBtn.disabled = false;
  }
});
