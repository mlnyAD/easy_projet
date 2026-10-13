

"use strict";

(function () {
    const panel = document.querySelector(
        "[data-ai-assistant-panel]"
    );

    if (!panel) {
        return;
    }

    const openButtons = document.querySelectorAll(
        "[data-ai-assistant-open]"
    );

    const closeButton = panel.querySelector(
        "[data-ai-assistant-close]"
    );

    const pinButton = panel.querySelector(
        "[data-ai-assistant-pin]"
    );

    const title = panel.querySelector(
        "[data-ai-assistant-title]"
    );

    const subtitle = panel.querySelector(
        "[data-ai-assistant-subtitle]"
    );

    const messages = panel.querySelector(
        "[data-ai-assistant-messages]"
    );

    const form = panel.querySelector(
        "[data-ai-assistant-form]"
    );

    const questionField = panel.querySelector(
        "[data-ai-assistant-question]"
    );

    const submitButton = panel.querySelector(
        "[data-ai-assistant-submit]"
    );

    const appMain = panel.closest(".ep-app-main");

    const desktopMedia = window.matchMedia(
        "(min-width: 1024px)"
    );

    const pinnedStorageKey = (
        "easy-projet-ai-assistant-pinned"
    );

    const histories = {
        general: [],
        planning: [],
    };

    let activeContext = "general";
    let activeEndpoint = (
        panel.dataset.aiAssistantGeneralUrl
        || ""
    );

    function refreshIcons() {
        if (
            window.lucide
            && typeof window.lucide.createIcons === "function"
        ) {
            window.lucide.createIcons();
        }
    }

    function isPinned() {
        return panel.classList.contains(
            "ep-ai-assistant-panel-pinned"
        );
    }

    function setOpen(isOpen) {
        if (isPinned() && desktopMedia.matches) {
            isOpen = true;
        }

        panel.classList.toggle(
            "ep-communication-panel-open",
            isOpen
        );

        panel.setAttribute(
            "aria-hidden",
            isOpen ? "false" : "true"
        );

        openButtons.forEach(function (button) {
            button.setAttribute(
                "aria-expanded",
                isOpen ? "true" : "false"
            );
        });

        if (isOpen && questionField) {
            questionField.focus();
        }
    }

    function setPinned(pinned, persist) {
        if (!desktopMedia.matches) {
            pinned = false;
        }

        panel.classList.toggle(
            "ep-ai-assistant-panel-pinned",
            pinned
        );

        if (appMain) {
            appMain.classList.toggle(
                "ep-app-main-ai-assistant-pinned",
                pinned
            );
        }

        if (pinButton) {
            pinButton.setAttribute(
                "aria-pressed",
                pinned ? "true" : "false"
            );

            pinButton.title = pinned
                ? "Désépingler le volet"
                : "Épingler le volet";

            pinButton.setAttribute(
                "aria-label",
                pinButton.title
            );
        }

        if (pinned) {
            setOpen(true);
        }

        if (persist) {
            localStorage.setItem(
                pinnedStorageKey,
                pinned ? "true" : "false"
            );
        }
    }

    function getContextIntro(context) {
        if (context === "planning") {
            return (
                "Sélectionnez un projet puis demandez une analyse "
                + "ou posez une question sur son planning."
            );
        }

        return (
            "Je peux vous aider à utiliser Easy Projet ou vous "
            + "proposer une méthode de travail."
        );
    }

    function appendMessage(role, content) {
        if (!messages) {
            return;
        }

        const message = document.createElement("div");

        message.className = (
            role === "user"
                ? "ep-ai-assistant-message ep-ai-assistant-message-user"
                : "ep-ai-assistant-message"
        );

        const label = document.createElement("p");

        label.className = "ep-ai-assistant-message-label";
        label.textContent = (
            role === "user"
                ? "Vous"
                : "Assistant IA"
        );

        const body = document.createElement("div");

        body.className = "ep-ai-assistant-message-body";
        body.textContent = content;

        message.append(label, body);
        messages.appendChild(message);
        messages.scrollTop = messages.scrollHeight;
    }

    function renderMessages() {
        if (!messages) {
            return;
        }

        messages.replaceChildren();

        appendMessage(
            "assistant",
            getContextIntro(activeContext)
        );

        histories[activeContext].forEach(function (message) {
            appendMessage(
                message.role,
                message.content
            );
        });
    }

    function setContext(button) {
        const context = (
            button.dataset.aiAssistantContext
            || "general"
        );

        activeContext = (
            context === "planning"
                ? "planning"
                : "general"
        );

        activeEndpoint = (
            button.dataset.aiAssistantEndpoint
            || panel.dataset.aiAssistantGeneralUrl
            || ""
        );

        if (title) {
            title.textContent = "Assistant IA";
        }

        if (subtitle) {
            subtitle.textContent = (
                activeContext === "planning"
                    ? "Analyse et recommandations de planning"
                    : "Questions générales sur Easy Projet"
            );
        }

        if (questionField) {
            questionField.value = "";
            questionField.placeholder = (
                activeContext === "planning"
                    ? (
                        "Ex. Quelles surcharges doivent être "
                        + "traitées en priorité ?"
                    )
                    : "Posez votre question…"
            );
        }

        renderMessages();
    }

    function getPlanningPayload() {
        const project = document.getElementById(
            "id_project"
        );

        const stateDate = document.getElementById(
            "id_state_date"
        );

        const dateFrom = document.getElementById(
            "id_date_from"
        );

        const dateTo = document.getElementById(
            "id_date_to"
        );

        return {
            project: project ? project.value : "",
            state_date: stateDate ? stateDate.value : "",
            date_from: dateFrom ? dateFrom.value : "",
            date_to: dateTo ? dateTo.value : "",
        };
    }

    function getCsrfToken() {
        const token = panel.querySelector(
            "[name='csrfmiddlewaretoken']"
        );

        return token ? token.value : "";
    }

    openButtons.forEach(function (button) {
        button.addEventListener(
            "click",
            function () {
                setContext(button);
                setOpen(true);
            }
        );
    });

    if (closeButton) {
        closeButton.addEventListener(
            "click",
            function () {
                if (isPinned()) {
                    setPinned(false, true);
                }

                setOpen(false);
            }
        );
    }

    if (pinButton) {
        pinButton.addEventListener(
            "click",
            function () {
                setPinned(
                    !isPinned(),
                    true
                );
            }
        );
    }

    if (form) {
        form.addEventListener(
            "submit",
            async function (event) {
                event.preventDefault();

                const question = (
                    questionField.value
                    || ""
                ).trim();

                if (!question) {
                    appendMessage(
                        "assistant",
                        "Saisissez une demande avant de continuer."
                    );
                    return;
                }

                if (
                    activeContext === "planning"
                    && !document.getElementById("id_project").value
                ) {
                    appendMessage(
                        "assistant",
                        "Sélectionnez un projet avant de lancer "
                        + "une analyse de planning."
                    );
                    return;
                }

                if (!activeEndpoint) {
                    appendMessage(
                        "assistant",
                        "Le service IA n'est pas configuré."
                    );
                    return;
                }

                const payload = {
                    question: question,
                    history: histories[activeContext],
                };

                if (activeContext === "planning") {
                    Object.assign(
                        payload,
                        getPlanningPayload()
                    );
                }

                appendMessage("user", question);

                if (submitButton) {
                    submitButton.disabled = true;
                }

                try {
                    const response = await fetch(
                        activeEndpoint,
                        {
                            method: "POST",
                            credentials: "same-origin",
                            headers: {
                                "Content-Type": "application/json",
                                "X-CSRFToken": getCsrfToken(),
                                "X-Requested-With": (
                                    "XMLHttpRequest"
                                ),
                            },
                            body: JSON.stringify(payload),
                        }
                    );

                    const data = await response.json();

                    if (!response.ok || !data.answer) {
                        throw new Error(
                            data.error
                            || "L'assistant n'a pas pu répondre."
                        );
                    }

                    histories[activeContext].push(
                        {
                            role: "user",
                            content: question,
                        },
                        {
                            role: "assistant",
                            content: data.answer,
                        }
                    );

                    appendMessage(
                        "assistant",
                        data.answer
                    );

                    questionField.value = "";
                } catch (error) {
                    appendMessage(
                        "assistant",
                        error.message
                        || "L'assistant n'a pas pu répondre."
                    );
                } finally {
                    if (submitButton) {
                        submitButton.disabled = false;
                    }
                }
            }
        );
    }

    desktopMedia.addEventListener(
        "change",
        function () {
            if (!desktopMedia.matches) {
                setPinned(false, false);
            }
        }
    );

    setPinned(
        localStorage.getItem(pinnedStorageKey) === "true",
        false
    );

    renderMessages();
}());