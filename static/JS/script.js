document.addEventListener("DOMContentLoaded", () => {
  const progress = document.getElementById("progress");
  const confidenceValue = document.getElementById("confidence-value");

  if (progress && confidenceValue) {
    // Get the raw confidence value
    let raw = progress.dataset.confidence.trim().replace('%', '');
    let value = parseFloat(raw);

    // Determine if it's in 0–1 range or 0–100 range
    let percentage = value <= 1 ? value * 100 : value;

    // Clamp between 0 and 100
    percentage = Math.max(0, Math.min(percentage, 100));

    // Update the text display
    confidenceValue.textContent = Math.round(percentage) + "%";

    // Set the bar width
    progress.style.width = percentage + "%";

    // Set color gradient based on confidence
    if (percentage >= 80) {
      progress.style.background = "linear-gradient(90deg, #00ff88, #00bfa6)";
    } else if (percentage >= 50) {
      progress.style.background = "linear-gradient(90deg, #ffbb00, #ff8800)";
    } else {
      progress.style.background = "linear-gradient(90deg, #ff4b2b, #ff416c)";
    }
  }
});
// 🌗 Theme Toggle
document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("theme-toggle");
  const body = document.body;

  // Load saved mode
  if (localStorage.getItem("theme") === "dark") {
    body.classList.add("dark-mode");
    toggle.textContent = "🌙 Dark Mode";
  } else {
    toggle.textContent = "🌞 Light Mode";
  }

  toggle.addEventListener("click", () => {
    body.classList.toggle("dark-mode");

    if (body.classList.contains("dark-mode")) {
      localStorage.setItem("theme", "dark");
      toggle.textContent = "🌙 Dark Mode";
    } else {
      localStorage.setItem("theme", "light");
      toggle.textContent = "🌞 Light Mode";
    }
  });
});
