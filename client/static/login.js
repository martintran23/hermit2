document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
  
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;
    const messageEl = document.getElementById("login-message");
  
    try {
      const res = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });
  
      const data = await res.json();
      messageEl.textContent = res.ok ? data.message : data.error;
      messageEl.style.color = res.ok ? "green" : "red";
  
      if (res.ok) {
        setTimeout(() => window.location.href = "/", 1000);
      }
    } catch (err) {
      console.error("Login error:", err);
      messageEl.textContent = "Login failed.";
      messageEl.style.color = "red";
    }
  });