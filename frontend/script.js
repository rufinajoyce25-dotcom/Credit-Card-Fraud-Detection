// -----------------------------
// SELECT ELEMENTS
// -----------------------------
const nameInput = document.querySelector("input[type='text']");
const passwordInput = document.querySelector("input[type='password']");
const amountInput = document.querySelector("input[type='number']");
const statusText = document.querySelector(".status-box p");

// Track registration status
let isRegistered = false;


// -----------------------------
// REGISTER FACE
// -----------------------------
function registerFace() {

    const name = nameInput.value.trim();
    const password = passwordInput.value.trim();

    if (!name || !password) {
        updateStatus("⚠ Enter name and password first", "orange");
        return;
    }

    updateStatus("📷 Registering face...", "#00c6ff");

    fetch("http://127.0.0.1:5000/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            name: name,
            password: password
        })
    })
    .then(response => response.json())
    .then(data => {

        if (data.status === "success") {
            isRegistered = true;
            updateStatus("✅ Face registered successfully", "#00ff00");
        } 
        else {
            updateStatus("❌ " + data.message, "red");
        }

    })
    .catch(error => {
        console.error(error);
        updateStatus("❌ Server error during registration", "red");
    });
}


// -----------------------------
// VERIFY (TRANSACTION)
// -----------------------------
function submitForm() {

    const name = nameInput.value.trim();
    const password = passwordInput.value.trim();
    const amount = amountInput.value.trim();

    // Validation
    if (!name || !password || !amount) {
        updateStatus("⚠ Please fill all fields", "orange");
        return;
    }

    // Ensure registration done
    if (!isRegistered) {
        updateStatus("⚠ Please register face first", "orange");
        return;
    }

    updateStatus("🔄 Verifying face and processing...", "#00c6ff");

    fetch("http://127.0.0.1:5000/transaction", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            name: name,
            password: password,
            amount: amount
        })
    })
    .then(response => response.json())
    .then(data => {

        if (data.status === "safe") {
            updateStatus("✅ SAFE TRANSACTION", "#00ff00");
        } 
        else if (data.status === "fraud") {
            updateStatus("🚨 SUSPICIOUS TRANSACTION", "red");
        } 
        else {
            updateStatus("❌ " + data.message, "orange");
        }

    })
    .catch(error => {
        console.error(error);
        updateStatus("❌ Server error during transaction", "red");
    });
}


// -----------------------------
// UPDATE STATUS FUNCTION
// -----------------------------
function updateStatus(message, color) {
    statusText.textContent = message;
    statusText.style.color = color;
}