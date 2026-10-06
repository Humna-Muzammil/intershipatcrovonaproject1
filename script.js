async function sendMessage() {

    const input = document.getElementById("message");
    const message = input.value.trim();

    if (message === "") {
        return;
    }

    addMessage("You", message);

    input.value = "";

    addMessage("AI", "Thinking...");

    const response = await fetch("/chat", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            message: message
        })

    });

    const data = await response.json();

    removeThinking();

    if (data.error) {

        addMessage("Error", data.error);

    } else {

        addMessage("AI", data.answer);

    }
}


function addMessage(sender, message) {

    const chatbox = document.getElementById("chatbox");

    const messageDiv = document.createElement("div");

    messageDiv.className =
        sender === "You"
        ? "user-message"
        : "ai-message";

    messageDiv.innerHTML =
        `<strong>${sender}:</strong><br>${message}`;

    chatbox.appendChild(messageDiv);

    chatbox.scrollTop = chatbox.scrollHeight;
}


function removeThinking() {

    const chatbox = document.getElementById("chatbox");

    const messages = chatbox.children;

    if (messages.length > 0) {

        const lastMessage =
            messages[messages.length - 1];

        if (lastMessage.innerText.includes("Thinking...")) {

            lastMessage.remove();

        }
    }
}


async function uploadDocument() {

    const fileInput =
        document.getElementById("file");

    const status =
        document.getElementById("uploadStatus");

    if (fileInput.files.length === 0) {

        status.innerText =
            "Please select a document.";

        return;
    }

    const formData = new FormData();

    formData.append(
        "file",
        fileInput.files[0]
    );


    status.innerText =
        "Uploading...";


    const response = await fetch("/upload", {

        method: "POST",

        body: formData

    });


    const data = await response.json();


    if (data.error) {

        status.innerText =
            "Error: " + data.error;

    } else {

        status.innerText =
            data.message +
            " (" +
            data.characters +
            " characters)";

    }
}


async function clearChat() {

    await fetch("/clear", {
        method: "POST"
    });

    document.getElementById("chatbox").innerHTML = "";

    document.getElementById("uploadStatus").innerText = "";
}