let token = localStorage.getItem("token");
if (token) {
    document.getElementById("at-container").innerHTML = `<span id="token">Your ID Token is <b>${token}</b></span>`;
}