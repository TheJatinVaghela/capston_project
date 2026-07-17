/**
 * SupportFlow embeddable chat widget
 * Usage:
 *   <script src="https://YOUR_API/widget.js" data-key="pk_xxx"></script>
 *
 * Features: themed chat, streaming replies, New chat, History (last chats).
 */
(function () {
  var script = document.currentScript;
  var key = script && script.getAttribute("data-key");
  if (!key) {
    console.error("[SupportFlow] Missing data-key on widget script");
    return;
  }

  var apiBase = (script.getAttribute("data-api") || script.src.replace(/\/widget\.js.*$/, "")).replace(/\/$/, "");
  var sessionKey = "sf_widget_session_" + key;
  var historyKey = "sf_widget_history_" + key;
  var HISTORY_MAX = 30;

  function newId() {
    return (
      (crypto.randomUUID && crypto.randomUUID()) ||
      "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
        var r = (Math.random() * 16) | 0;
        var v = c === "x" ? r : (r & 0x3) | 0x8;
        return v.toString(16);
      })
    );
  }

  function loadHistory() {
    try {
      var raw = localStorage.getItem(historyKey);
      var list = raw ? JSON.parse(raw) : [];
      return Array.isArray(list) ? list : [];
    } catch (e) {
      return [];
    }
  }

  function saveHistory(list) {
    try {
      localStorage.setItem(historyKey, JSON.stringify((list || []).slice(0, HISTORY_MAX)));
    } catch (e) {}
  }

  function touchHistory(sessionId, preview) {
    if (!sessionId) return;
    var list = loadHistory().filter(function (h) {
      return h && h.id !== sessionId;
    });
    list.unshift({
      id: sessionId,
      preview: (preview || "Conversation").toString().trim().slice(0, 80) || "Conversation",
      updated_at: new Date().toISOString(),
    });
    saveHistory(list);
  }

  function ensureInHistory(sessionId) {
    if (!sessionId) return;
    var list = loadHistory();
    var found = list.some(function (h) {
      return h && h.id === sessionId;
    });
    if (!found) {
      list.unshift({
        id: sessionId,
        preview: "New chat",
        updated_at: new Date().toISOString(),
      });
      saveHistory(list);
    }
  }

  var sessionId = localStorage.getItem(sessionKey);
  if (!sessionId) {
    sessionId = newId();
    localStorage.setItem(sessionKey, sessionId);
  }

  var cfg = { business_name: "Support", tagline: "Chat with us", active: false };
  var theme = {
    primary: "#0d6efd",
    header: "#0d6efd",
    user_bubble: "#0d6efd",
    accent: "#2dd4bf",
  };
  var welcomeShown = false;
  var historyOpen = false;
  var busy = false;

  function applyTheme(colors) {
    if (!colors) return;
    if (colors.primary) theme.primary = colors.primary;
    if (colors.header) theme.header = colors.header;
    if (colors.user_bubble) theme.user_bubble = colors.user_bubble;
    if (colors.accent) theme.accent = colors.accent;
    btn.style.background = theme.primary;
    sendBtn.style.background = theme.primary;
    if (headerBar) headerBar.style.background = theme.header;
    if (historyHeader) historyHeader.style.background = theme.header;
    if (newChatBtn) {
      newChatBtn.style.background = "rgba(255,255,255,0.18)";
    }
  }

  function el(tag, attrs, children) {
    var n = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        if (k === "style" && typeof attrs[k] === "object") {
          Object.assign(n.style, attrs[k]);
        } else if (k === "text") {
          n.textContent = attrs[k];
        } else if (k.indexOf("on") === 0) {
          n.addEventListener(k.slice(2).toLowerCase(), attrs[k]);
        } else {
          n.setAttribute(k, attrs[k]);
        }
      });
    }
    (children || []).forEach(function (c) {
      if (c) n.appendChild(c);
    });
    return n;
  }

  function clearMessages() {
    while (messages.firstChild) messages.removeChild(messages.firstChild);
  }

  function addMsg(box, role, text) {
    var row = el("div", {
      style: {
        display: "flex",
        justifyContent: role === "user" ? "flex-end" : "flex-start",
        marginBottom: "8px",
      },
    });
    var bubble = el("div", {
      text: text,
      style: {
        maxWidth: "85%",
        padding: "8px 12px",
        borderRadius: "12px",
        fontSize: "14px",
        lineHeight: "1.4",
        whiteSpace: "pre-wrap",
        background: role === "user" ? theme.user_bubble : "#f1f3f5",
        color: role === "user" ? "#fff" : "#212529",
      },
    });
    row.appendChild(bubble);
    box.appendChild(row);
    box.scrollTop = box.scrollHeight;
    return bubble;
  }

  function welcomeText() {
    return (
      "Hi! I'm the support assistant for " +
      (cfg.business_name || "this store") +
      ". How can I help with your order, products, or account?"
    );
  }

  function showWelcome() {
    clearMessages();
    addMsg(messages, "bot", welcomeText());
    welcomeShown = true;
  }

  function setSession(id) {
    sessionId = id;
    localStorage.setItem(sessionKey, id);
  }

  function formatWhen(iso) {
    if (!iso) return "";
    try {
      var d = new Date(iso);
      return d.toLocaleString([], {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch (e) {
      return "";
    }
  }

  function renderHistoryList() {
    while (historyList.firstChild) historyList.removeChild(historyList.firstChild);
    var list = loadHistory();
    if (!list.length) {
      historyList.appendChild(
        el("div", {
          text: "No past chats yet. Start a conversation and it will show up here.",
          style: {
            padding: "16px",
            fontSize: "13px",
            color: "#6c757d",
            lineHeight: "1.45",
          },
        })
      );
      return;
    }
    list.forEach(function (item) {
      var active = item.id === sessionId;
      var row = el(
        "button",
        {
          type: "button",
          style: {
            display: "block",
            width: "100%",
            textAlign: "left",
            border: "none",
            borderBottom: "1px solid #e9ecef",
            background: active ? "#e7f1ff" : "#fff",
            padding: "12px 14px",
            cursor: "pointer",
            fontFamily: "inherit",
          },
          onClick: function () {
            selectHistory(item.id);
          },
        },
        [
          el("div", {
            text: item.preview || "Conversation",
            style: {
              fontSize: "13px",
              fontWeight: active ? "700" : "500",
              color: "#212529",
              marginBottom: "4px",
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
            },
          }),
          el("div", {
            text: (active ? "Current · " : "") + formatWhen(item.updated_at),
            style: { fontSize: "11px", color: "#868e96" },
          }),
        ]
      );
      historyList.appendChild(row);
    });
  }

  function openHistory() {
    historyOpen = true;
    historyPanel.style.display = "flex";
    renderHistoryList();
  }

  function closeHistory() {
    historyOpen = false;
    historyPanel.style.display = "none";
  }

  function loadSessionMessages(id, opts) {
    opts = opts || {};
    busy = true;
    return fetch(
      apiBase +
        "/embed/sessions/" +
        encodeURIComponent(id) +
        "/messages?key=" +
        encodeURIComponent(key)
    )
      .then(function (r) {
        return r.json().then(function (j) {
          return { ok: r.ok, j: j };
        });
      })
      .then(function (res) {
        clearMessages();
        if (!res.ok) {
          showWelcome();
          return;
        }
        var msgs = res.j.messages || [];
        if (!msgs.length) {
          showWelcome();
          return;
        }
        msgs.forEach(function (m) {
          addMsg(messages, m.role === "user" ? "user" : "bot", m.content || "");
        });
        welcomeShown = true;
        var firstUser = msgs.filter(function (m) {
          return m.role === "user";
        })[0];
        if (firstUser) touchHistory(id, firstUser.content);
      })
      .catch(function () {
        if (opts.fallbackWelcome !== false) showWelcome();
      })
      .finally(function () {
        busy = false;
      });
  }

  function selectHistory(id) {
    if (!id || busy) return;
    setSession(id);
    closeHistory();
    loadSessionMessages(id);
  }

  function startNewChat() {
    if (busy) return;
    closeHistory();
    var id = newId();
    setSession(id);
    showWelcome();
    touchHistory(id, "New chat");
  }

  function openPanel() {
    panel.style.display = "flex";
    btn.style.display = "none";
  }
  function closePanel() {
    closeHistory();
    panel.style.display = "none";
    btn.style.display = "flex";
  }

  var btn = el("button", {
    type: "button",
    "aria-label": "Open chat",
    style: {
      position: "fixed",
      right: "20px",
      bottom: "20px",
      width: "56px",
      height: "56px",
      borderRadius: "50%",
      border: "none",
      background: "#0d6efd",
      color: "#fff",
      fontSize: "22px",
      cursor: "pointer",
      boxShadow: "0 4px 16px rgba(0,0,0,0.2)",
      zIndex: "2147483000",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
    },
    onClick: openPanel,
    text: "💬",
  });

  var messages = el("div", {
    style: {
      flex: "1",
      overflowY: "auto",
      padding: "12px",
      background: "#fff",
      position: "relative",
    },
  });

  var input = el("input", {
    type: "text",
    placeholder: "Type a message…",
    style: {
      flex: "1",
      border: "1px solid #dee2e6",
      borderRadius: "8px",
      padding: "10px 12px",
      fontSize: "14px",
      outline: "none",
    },
  });

  var sendBtn = el("button", {
    type: "button",
    text: "Send",
    style: {
      border: "none",
      background: "#0d6efd",
      color: "#fff",
      borderRadius: "8px",
      padding: "10px 14px",
      cursor: "pointer",
      fontWeight: "600",
    },
  });

  var headerTitle = el("div", {
    text: "Support",
    style: { fontWeight: "700", fontSize: "15px" },
  });
  var headerSub = el("div", {
    text: "Customer support",
    style: { fontSize: "12px", opacity: "0.85" },
  });

  function iconBtn(label, title, onClick) {
    return el("button", {
      type: "button",
      text: label,
      title: title,
      "aria-label": title,
      onClick: onClick,
      style: {
        background: "rgba(255,255,255,0.18)",
        border: "1px solid rgba(255,255,255,0.35)",
        color: "#fff",
        borderRadius: "8px",
        padding: "4px 8px",
        cursor: "pointer",
        fontSize: "12px",
        fontWeight: "600",
        lineHeight: "1.2",
      },
    });
  }

  var historyBtn = iconBtn("History", "Past chats", function () {
    if (historyOpen) closeHistory();
    else openHistory();
  });
  var newChatBtn = iconBtn("New", "Start a new chat", startNewChat);
  var closeBtn = el("button", {
    type: "button",
    text: "×",
    title: "Close",
    onClick: closePanel,
    style: {
      background: "transparent",
      border: "none",
      color: "#fff",
      fontSize: "24px",
      cursor: "pointer",
      lineHeight: "1",
      padding: "0 2px",
    },
  });

  var headerBar = el(
    "div",
    {
      style: {
        background: theme.header,
        color: "#fff",
        padding: "12px 12px 12px 16px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        gap: "8px",
      },
    },
    [
      el("div", { style: { minWidth: 0, flex: "1" } }, [headerTitle, headerSub]),
      el(
        "div",
        {
          style: {
            display: "flex",
            alignItems: "center",
            gap: "6px",
            flexShrink: "0",
          },
        },
        [historyBtn, newChatBtn, closeBtn]
      ),
    ]
  );

  var historyList = el("div", {
    style: { flex: "1", overflowY: "auto", background: "#fff" },
  });
  var historyHeader = el(
    "div",
    {
      style: {
        background: theme.header,
        color: "#fff",
        padding: "12px 14px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      },
    },
    [
      el("div", {
        text: "Chat history",
        style: { fontWeight: "700", fontSize: "14px" },
      }),
      el("button", {
        type: "button",
        text: "Back",
        onClick: closeHistory,
        style: {
          background: "rgba(255,255,255,0.18)",
          border: "1px solid rgba(255,255,255,0.35)",
          color: "#fff",
          borderRadius: "8px",
          padding: "4px 10px",
          cursor: "pointer",
          fontSize: "12px",
          fontWeight: "600",
        },
      }),
    ]
  );
  var historyPanel = el(
    "div",
    {
      style: {
        position: "absolute",
        inset: "0",
        display: "none",
        flexDirection: "column",
        background: "#fff",
        zIndex: "2",
      },
    },
    [historyHeader, historyList]
  );

  var chatBody = el(
    "div",
    {
      style: {
        flex: "1",
        display: "flex",
        flexDirection: "column",
        minHeight: "0",
        position: "relative",
      },
    },
    [messages, historyPanel]
  );

  var panel = el(
    "div",
    {
      style: {
        position: "fixed",
        right: "20px",
        bottom: "20px",
        width: "360px",
        maxWidth: "calc(100vw - 24px)",
        height: "520px",
        maxHeight: "calc(100vh - 40px)",
        background: "#fff",
        borderRadius: "16px",
        boxShadow: "0 12px 40px rgba(0,0,0,0.25)",
        zIndex: "2147483000",
        display: "none",
        flexDirection: "column",
        overflow: "hidden",
        fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
      },
    },
    [
      headerBar,
      chatBody,
      el(
        "div",
        {
          style: {
            display: "flex",
            gap: "8px",
            padding: "12px",
            borderTop: "1px solid #e9ecef",
          },
        },
        [input, sendBtn]
      ),
    ]
  );

  function send() {
    var text = (input.value || "").trim();
    if (!text || busy) return;
    input.value = "";
    closeHistory();
    addMsg(messages, "user", text);
    touchHistory(sessionId, text);
    sendBtn.disabled = true;
    busy = true;
    var botBubble = addMsg(messages, "bot", "…");

    fetch(apiBase + "/chat/stream?key=" + encodeURIComponent(key), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Widget-Key": key,
      },
      body: JSON.stringify({
        message: text,
        widget_key: key,
        session_id: sessionId,
        source: "widget",
      }),
    })
      .then(function (r) {
        if (!r.ok) {
          return r.json().then(function (j) {
            throw new Error((j && j.error) || "Sorry, something went wrong.");
          });
        }
        if (!r.body || !r.body.getReader) {
          throw new Error("Streaming not supported in this browser.");
        }
        var reader = r.body.getReader();
        var decoder = new TextDecoder();
        var buffer = "";
        var started = false;

        function readChunk() {
          return reader.read().then(function (result) {
            if (result.done) return;
            buffer += decoder.decode(result.value, { stream: true });
            var parts = buffer.split("\n\n");
            buffer = parts.pop() || "";
            parts.forEach(function (block) {
              var line = block.trim();
              if (line.indexOf("data:") !== 0) return;
              var jsonStr = line.replace(/^data:\s*/, "");
              var event;
              try {
                event = JSON.parse(jsonStr);
              } catch (e) {
                return;
              }
              if (event.type === "token" && event.text) {
                if (!started) {
                  botBubble.textContent = "";
                  started = true;
                }
                botBubble.textContent += event.text;
                messages.scrollTop = messages.scrollHeight;
              } else if (event.type === "done" && event.response) {
                botBubble.textContent = event.response;
                messages.scrollTop = messages.scrollHeight;
              } else if (event.type === "error") {
                throw new Error(event.error || "Stream error");
              }
            });
            return readChunk();
          });
        }
        return readChunk();
      })
      .catch(function (err) {
        botBubble.textContent =
          (err && err.message) || "Could not reach support. Please try again later.";
      })
      .finally(function () {
        sendBtn.disabled = false;
        busy = false;
      });
  }

  sendBtn.addEventListener("click", send);
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") send();
  });

  document.body.appendChild(btn);
  document.body.appendChild(panel);

  // Ensure current session is in history list (without wiping preview)
  ensureInHistory(sessionId);

  fetch(apiBase + "/embed/config?key=" + encodeURIComponent(key))
    .then(function (r) {
      return r.json().then(function (j) {
        return { ok: r.ok, j: j };
      });
    })
    .then(function (res) {
      if (!res.ok || !res.j.active) {
        headerTitle.textContent = "Unavailable";
        headerSub.textContent = res.j.error || "Subscription inactive";
        addMsg(
          messages,
          "bot",
          "This chat widget is not active. Please ask the site owner to subscribe."
        );
        return;
      }
      cfg = res.j;
      headerTitle.textContent = cfg.business_name || "Support";
      headerSub.textContent = cfg.tagline || "Customer support";
      applyTheme(cfg.chat_colors);
      // Resume last chat if it has messages; otherwise welcome
      return loadSessionMessages(sessionId, { fallbackWelcome: true });
    })
    .catch(function () {
      addMsg(messages, "bot", "Unable to load chat configuration.");
    });
})();
