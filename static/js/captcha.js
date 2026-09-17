document.addEventListener("DOMContentLoaded", () => {
  const captchaBtn = document.getElementById("captcha-btn");
  const captchaBox = document.getElementById("captcha-box");
  const captchaLabel = document.getElementById("captcha-label");
  const captchaTokenInput = document.getElementById("captcha-token");

  if (!captchaBtn || !captchaTokenInput) return;

  captchaBtn.addEventListener("click", async () => {
    if (captchaTokenInput.value) return;

    captchaLabel.textContent = "Verifying...";
    captchaBtn.style.opacity = "0.7";

    try {
      const resp = await fetch("/api/captcha-token");
      if (!resp.ok) {
        throw new Error("Verification request failed");
      }
      const data = await resp.json();
      if (!data.token) {
        throw new Error("Missing token in response");
      }

      captchaTokenInput.value = data.token;
      captchaBox.classList.add("checked");
      captchaBox.innerHTML = "&#10003;";
      captchaLabel.textContent = "Verified human";
      captchaBtn.classList.add("captcha-verified");
      captchaBtn.style.opacity = "1";
      captchaBtn.setAttribute("aria-pressed", "true");
    } catch (err) {
      console.error("Captcha error:", err);
      captchaLabel.textContent = "Verification failed. Click to retry.";
      captchaBtn.style.opacity = "1";
    }
  });
});
