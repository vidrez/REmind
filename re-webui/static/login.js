let token = localStorage.getItem("token");
if (!token) {
    console.log(document.getElementById("signup"))
    document.getElementById("signup").classList.remove("d-none");
} else {
    fetch("/auth/token/validate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ token: token })
    })
        .then(response => response.json())
        .then(data => {
            console.log(data)
            if (data.valid) {
                document.getElementById("token").value = token;
            } else {
                generateToken();
            }
        })
        .catch(error => {
            console.error("Error validating token:", error);
            generateToken();
        });
}

let generateToken = () => {
    document.getElementById("signup").setAttribute('disabled', '');
    fetch("/auth/token", {
        method: "POST"
    })
        .then(response => response.json())
        .then(data => {
            token = data.token;
            localStorage.setItem("token", token);
            document.getElementById("token").value = token;
            document.getElementById("signup").classList.add("d-none");
        })
        .catch(error => console.error("Error fetching token:", error));
};