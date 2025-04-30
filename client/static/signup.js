document.getElementById("signup-form").addEventListener("submit", async (e) => {
    e.preventDefault();
  
    const email = document.getElementById("signup-email").value;
    const password = document.getElementById("signup-password").value;
    const messageEl = document.getElementById("signup-message");
  
    try {
      const res = await fetch("/api/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });
  
      const data = await res.json();
      messageEl.textContent = res.ok ? data.message : data.error;
      messageEl.style.color = res.ok ? "green" : "red";
    } catch (err) {
      console.error("Signup error:", err);
      messageEl.textContent = "Signup failed. Try again.";
      messageEl.style.color = "red";
    }
  });