const tokenInput = document.getElementById("token");
const signupBtn = document.getElementById("signup");
const signinBtn = document.getElementById("signin");

const updateButtonState = () => {
    if (tokenInput.value.trim().length > 0) {
        signupBtn.setAttribute('disabled', '');
        signinBtn.removeAttribute('disabled');
    } else {
        signinBtn.setAttribute('disabled', '');
        signupBtn.removeAttribute('disabled');
    }
};

tokenInput.addEventListener("input", updateButtonState);


let token = localStorage.getItem("token");

if (token) {
    tokenInput.value = token;
    updateButtonState();

    fetch("/auth/token/validate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
        },
        body: JSON.stringify({ token: token })
    })
        .then(response => response.json())
        .then(data => {
            if (data.valid) {
                document.getElementById("at-container").innerHTML = `<span id="token">Your ID Token is <b>${token}</b></span>`;
                updateButtonState();
            } else {
                generateToken();
            }
        })
        .catch(error => {
            console.error("Error validating token:", error);
            generateToken();
        });
} else {
    updateButtonState();
}

let generateToken = () => {
    signupBtn.setAttribute('disabled', '');

    fetch("/auth/token", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
        }
    })
        .then(response => response.json())
        .then(data => {
            token = data.token;
            localStorage.setItem("token", token);

            tokenInput.value = token;
            document.getElementById("at-container").innerHTML = `<span id="token">Your ID Token is <b>${token}</b></span>`;
            updateButtonState();
        })
        .catch(error => console.error("Error fetching token:", error));
};