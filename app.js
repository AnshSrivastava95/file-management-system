// ================= GLOBAL =================
let currentEmail = "";

// ================= SAFE GET =================
function get(id) {
    return document.getElementById(id);
}

// ================= UI SWITCH =================
function showRegister() {
    get("loginSection")?.style.setProperty("display", "none");
    get("registerSection")?.style.setProperty("display", "block");
}

function showLogin() {
    get("loginSection")?.style.setProperty("display", "block");
    get("registerSection")?.style.setProperty("display", "none");
    get("otpSection")?.style.setProperty("display", "none");
}

// ================= REGISTER =================
async function register() {
    const email = get("regEmail")?.value;
    const password = get("regPassword")?.value;

    if (!email || !password) {
        alert("Enter email and password");
        return;
    }

    try {
        const res = await fetch("http://127.0.0.1:8000/register", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.detail || data.error);
            return;
        }

        alert("Registered successfully");
        showLogin();

    } catch (err) {
        console.error(err);
        alert("Backend not running");
    }
}

// ================= LOGIN =================
async function login() {
    const email = get("email")?.value;
    const password = get("password")?.value;

    if (!email || !password) {
        alert("Enter email and password");
        return;
    }

    currentEmail = email;

    try {
        const res = await fetch("http://127.0.0.1:8000/login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.detail || data.error);
            return;
        }

        get("loginSection").style.display = "none";
        get("otpSection").style.display = "block";

    } catch (err) {
        console.error(err);
        alert("Backend not running");
    }
}

// ================= VERIFY OTP =================
async function verifyOTP() {
    const otp = get("otp")?.value;

    if (!otp) {
        alert("Enter OTP");
        return;
    }

    try {
        const res = await fetch("http://127.0.0.1:8000/verify-otp", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ email: currentEmail, otp })
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.detail || data.error);
            return;
        }

        if (data.session) {
            localStorage.setItem("session", data.session);
            window.location.href = "dashboard.html";
        }

    } catch (err) {
        console.error(err);
        alert("Backend not running");
    }
}

// ================= LOAD FILES =================
async function loadFiles() {
    try {
        const res = await fetch("http://127.0.0.1:8000/file/list", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                session: localStorage.getItem("session")
            })
        });

        const data = await res.json();

        if (data.files) {
            renderFiles(data.files);
        }

    } catch (err) {
        console.error("Error loading files:", err);
    }
}

// ================= RENDER FILES =================
function renderFiles(files) {
    const container = get("fileList");
    if (!container) return;

    container.innerHTML = "";

    files.forEach(file => {
        const div = document.createElement("div");
        div.className = "file-item";

        const name = document.createElement("span");
        name.innerText = file;
        name.onclick = () => readFile(file);

        const del = document.createElement("button");
        del.innerText = "X";
        del.className = "delete-btn";

        del.onclick = (e) => {
            e.stopPropagation();
            deleteFile(file);
        };

        div.appendChild(name);
        div.appendChild(del);
        container.appendChild(div);
    });
}

// ================= CREATE FILE =================
async function createFile() {
    const filename = get("filename")?.value;
    const content = get("content")?.value;

    if (!filename) {
        alert("Enter filename");
        return;
    }

    try {
        const res = await fetch("http://127.0.0.1:8000/file/create", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                session: localStorage.getItem("session"),
                filename,
                content
            })
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.detail || data.error);
            return;
        }

        // clear inputs
        get("filename").value = "";
        get("content").value = "";

        loadFiles();

    } catch (err) {
        console.error(err);
    }
}

// ================= READ FILE =================
async function readFile(filename) {
    try {
        const res = await fetch("http://127.0.0.1:8000/file/read", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                session: localStorage.getItem("session"),
                filename
            })
        });

        const data = await res.json();

        const viewer = get("fileViewer");
        if (viewer) {
            viewer.innerText = data.content || data.error;
        }

    } catch (err) {
        console.error(err);
    }
}

// ================= DELETE FILE =================
async function deleteFile(filename) {
    try {
        const res = await fetch("http://127.0.0.1:8000/file/delete", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                session: localStorage.getItem("session"),
                filename
            })
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.detail || data.error);
            return;
        }

        loadFiles();

    } catch (err) {
        console.error(err);
    }
}

async function checkRole() {
    const res = await fetch("http://127.0.0.1:8000/me", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            session: localStorage.getItem("session")
        })
    });

    const data = await res.json();

    if (data.role === "superadmin") {
        document.getElementById("adminPanel").style.display = "block";
    }
}

async function setRole() {
    const email = document.getElementById("targetEmail").value;
    const role = document.getElementById("roleSelect").value;

    const res = await fetch("http://127.0.0.1:8000/admin/set-role", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            session: localStorage.getItem("session"),
            email,
            role
        })
    });

    const data = await res.json();
    alert(data.message || data.error);
}

// ================= LOGOUT =================
function logout() {
    localStorage.removeItem("session");
    window.location.href = "index.html";
}

// ================= AUTO LOAD =================
window.onload = function () {
    if (get("fileList")) {
        loadFiles();
        checkRole();
    }
};