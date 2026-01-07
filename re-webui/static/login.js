let token = localStorage.getItem("token");
if (token) {
    document.getElementById("signup").setAttribute('disabled', '');
    document.getElementById("signin").removeAttribute('disabled');

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
                document.getElementById("token").value = token;
                document.getElementById("at-container").innerHTML = `<span id="token">Your ID Token is <b>${token}</b></span>`;
            } else {
                generateToken();
            }
        })
        .catch(error => {
            console.error("Error validating token:", error);
            generateToken();
        });
} else {
    document.getElementById("signin").setAttribute('disabled', '');
    document.getElementById("signup").removeAttribute('disabled');
}

let generateToken = () => {
    document.getElementById("signup").setAttribute('disabled', '');
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
            document.getElementById("token").value = token;
            document.getElementById("at-container").innerHTML = `<span id="token">Your ID Token is <b>${token}</b></span>`;
            document.getElementById("signup").setAttribute('disabled', '');
            document.getElementById("signin").removeAttribute('disabled');
        })
        .catch(error => console.error("Error fetching token:", error));
};