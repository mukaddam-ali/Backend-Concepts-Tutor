const STORAGE_KEY = "ragChatState";

const SUGGESTION_POOL = [
  "What is a REST API and what are its core principles?",
  "What is the difference between SQL and NoSQL databases?",
  "Why would I use caching?",
  "What is database sharding?",
  "How does a message queue work?",
  "What is CORS and why does it exist?",
  "When should I use microservices instead of a monolith?",
  "What is the difference between authentication and authorization?",
  "What is the N+1 query problem?",
  "What is the CAP theorem?",
  "What is a circuit breaker?",
  "What is Kubernetes used for?",
  "What is serverless computing?",
  "How does RAG (Retrieval-Augmented Generation) work?",
  "What is the Twelve-Factor App?",
  "What is a reverse proxy?",
];

const messagesEl = document.getElementById("messages");
const emptyStateEl = document.getElementById("empty-state");
const suggestionsEl = document.getElementById("suggestions");
const conversationListEl = document.getElementById("conversation-list");
const formEl = document.getElementById("chat-form");
const inputEl = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const statusDot = document.getElementById("status-dot");
const statusText = document.getElementById("status-text");
const newChatBtn = document.getElementById("new-chat-btn");
const sidebarEl = document.getElementById("sidebar");
const sidebarToggleBtn = document.getElementById("sidebar-toggle");
const sidebarOverlayEl = document.getElementById("sidebar-overlay");

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {
    /* fall through to fresh state */
  }
  return { conversations: [], activeId: null };
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

let state = loadState();

function makeId() {
  return crypto.randomUUID ? crypto.randomUUID() : String(Date.now()) + Math.random();
}

function getActiveConversation() {
  return state.conversations.find((c) => c.id === state.activeId) || null;
}

function titleFromMessage(text) {
  const trimmed = text.trim();
  return trimmed.length > 42 ? trimmed.slice(0, 42) + "…" : trimmed;
}

function createNewConversation({ activate = true } = {}) {
  const conversation = { id: makeId(), title: null, messages: [] };
  state.conversations.unshift(conversation);
  if (activate) state.activeId = conversation.id;
  saveState();
  return conversation;
}

function deleteConversation(id) {
  state.conversations = state.conversations.filter((c) => c.id !== id);
  if (state.activeId === id) {
    state.activeId = state.conversations[0]?.id ?? null;
  }
  saveState();
  renderSidebar();
  renderActiveConversation();
}

function selectConversation(id) {
  state.activeId = id;
  saveState();
  renderSidebar();
  renderActiveConversation();
  closeMobileSidebar();
}

function renderSidebar() {
  conversationListEl.innerHTML = "";
  state.conversations.forEach((conversation) => {
    const item = document.createElement("div");
    item.className = "conversation-item" + (conversation.id === state.activeId ? " active" : "");

    const title = document.createElement("span");
    title.className = "title";
    title.textContent = conversation.title || "New chat";
    item.appendChild(title);

    const deleteBtn = document.createElement("span");
    deleteBtn.className = "delete-btn";
    deleteBtn.innerHTML =
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-3.5 h-3.5"><path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0-1 14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2L4 6"/></svg>';
    deleteBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      deleteConversation(conversation.id);
    });
    item.appendChild(deleteBtn);

    item.addEventListener("click", () => selectConversation(conversation.id));
    conversationListEl.appendChild(item);
  });
}

function pickSuggestions(count) {
  const shuffled = [...SUGGESTION_POOL].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, count);
}

function renderSuggestions() {
  suggestionsEl.innerHTML = "";
  pickSuggestions(4).forEach((text) => {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "suggestion-card";
    card.textContent = text;
    card.addEventListener("click", () => sendMessage(text));
    suggestionsEl.appendChild(card);
  });
}

function scrollToBottom() {
  const chat = document.getElementById("chat");
  chat.scrollTop = chat.scrollHeight;
}

function buildUserBubble(text) {
  const row = document.createElement("div");
  row.className = "message-row user";
  const bubble = document.createElement("div");
  bubble.className = "bubble user";
  bubble.textContent = text;
  row.appendChild(bubble);
  return row;
}

function buildAssistantBubble({ answer, sources, isDemo }, { pending = false } = {}) {
  const row = document.createElement("div");
  row.className = "message-row assistant";

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.innerHTML =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-3.5 h-3.5"><path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2Z"/><path d="M8 12h8M12 8v8"/></svg>';
  row.appendChild(avatar);

  const content = document.createElement("div");
  content.className = "assistant-content";

  if (pending) {
    content.innerHTML =
      '<span class="typing-dot">&bull;</span> <span class="typing-dot">&bull;</span> <span class="typing-dot">&bull;</span>';
    row.appendChild(content);
    return row;
  }

  if (isDemo) {
    const tag = document.createElement("span");
    tag.className = "demo-tag";
    tag.textContent = "Demo mode";
    content.appendChild(tag);
    content.appendChild(document.createElement("br"));
  }

  const answerText = document.createElement("span");
  answerText.textContent = answer.replace(/^\[DEMO MODE.*?\]\n/s, "");
  content.appendChild(answerText);

  if (sources && sources.length > 0) {
    const sourcesEl = document.createElement("div");
    sourcesEl.className = "sources";
    sourcesEl.appendChild(document.createTextNode("Sources: "));
    sources.forEach((s) => {
      const chip = document.createElement("span");
      chip.className = "source-chip";
      chip.textContent = s;
      sourcesEl.appendChild(chip);
    });
    content.appendChild(sourcesEl);
  }

  row.appendChild(content);
  return row;
}

function buildErrorBubble(text) {
  const row = document.createElement("div");
  row.className = "message-row assistant";
  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.style.background = "var(--destructive)";
  avatar.innerHTML =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-3.5 h-3.5"><path d="M12 9v4M12 17h.01M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z"/></svg>';
  row.appendChild(avatar);
  const content = document.createElement("div");
  content.className = "assistant-content";
  content.style.color = "var(--destructive)";
  content.textContent = text;
  row.appendChild(content);
  return row;
}

function renderActiveConversation() {
  const conversation = getActiveConversation();

  if (!conversation || conversation.messages.length === 0) {
    emptyStateEl.classList.remove("hidden");
    messagesEl.classList.add("hidden");
    messagesEl.innerHTML = "";
    renderSuggestions();
    return;
  }

  emptyStateEl.classList.add("hidden");
  messagesEl.classList.remove("hidden");
  messagesEl.innerHTML = "";

  conversation.messages.forEach((msg) => {
    if (msg.role === "user") {
      messagesEl.appendChild(buildUserBubble(msg.content));
    } else {
      messagesEl.appendChild(
        buildAssistantBubble({
          answer: msg.content,
          sources: msg.sources,
          isDemo: msg.content.startsWith("[DEMO MODE"),
        })
      );
    }
  });

  scrollToBottom();
}

async function sendMessage(text) {
  let conversation = getActiveConversation();
  if (!conversation) {
    conversation = createNewConversation();
  }
  if (!conversation.title) {
    conversation.title = titleFromMessage(text);
  }
  conversation.messages.push({ role: "user", content: text });
  saveState();
  renderSidebar();
  renderActiveConversation();

  const pendingRow = buildAssistantBubble({}, { pending: true });
  messagesEl.appendChild(pendingRow);
  scrollToBottom();
  sendBtn.disabled = true;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });

    if (!res.ok) throw new Error(`Server returned ${res.status}`);

    const data = await res.json();
    pendingRow.remove();
    conversation.messages.push({ role: "assistant", content: data.answer, sources: data.sources });
    saveState();
    messagesEl.appendChild(
      buildAssistantBubble({
        answer: data.answer,
        sources: data.sources,
        isDemo: data.answer.startsWith("[DEMO MODE"),
      })
    );
    scrollToBottom();
  } catch (err) {
    pendingRow.remove();
    messagesEl.appendChild(
      buildErrorBubble("Something went wrong reaching the backend. Is the server still running?")
    );
    scrollToBottom();
    console.error(err);
  } finally {
    sendBtn.disabled = false;
    inputEl.focus();
  }
}

formEl.addEventListener("submit", (e) => {
  e.preventDefault();
  const message = inputEl.value.trim();
  if (!message) return;
  inputEl.value = "";
  sendMessage(message);
});

inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    formEl.requestSubmit();
  }
});

newChatBtn.addEventListener("click", () => {
  state.activeId = null;
  saveState();
  renderSidebar();
  renderActiveConversation();
  closeMobileSidebar();
  inputEl.focus();
});

function openMobileSidebar() {
  sidebarEl.classList.remove("-translate-x-full");
  sidebarOverlayEl.classList.remove("hidden");
}
function closeMobileSidebar() {
  sidebarEl.classList.add("-translate-x-full");
  sidebarOverlayEl.classList.add("hidden");
}
sidebarToggleBtn.addEventListener("click", () => {
  const isOpen = !sidebarEl.classList.contains("-translate-x-full");
  isOpen ? closeMobileSidebar() : openMobileSidebar();
});
sidebarOverlayEl.addEventListener("click", closeMobileSidebar);

async function loadStatus() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    if (data.backend === "demo") {
      statusDot.style.background = "var(--destructive)";
      statusText.textContent = `Demo mode · ${data.chunk_count} chunks`;
    } else {
      statusDot.style.background = "var(--primary)";
      statusText.textContent = `Foundry Local · ${data.chunk_count} chunks`;
    }
  } catch {
    statusText.textContent = "Backend unreachable";
  }
}

renderSidebar();
renderActiveConversation();
loadStatus();
inputEl.focus();
