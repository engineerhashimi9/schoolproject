// Get DOM elements

const openBtn = document.getElementById("test");

const modal = document.getElementById("msgBoxModal");

const closeBtn = document.getElementById("closeBoxBtn");

// Show the message box when clicking the trigger button
openBtn.onclick = function () {
  alert("buttone pressed");
  modal.style.display = "flex";
};

// Hide the message box when clicking the close button
closeBtn.addEventListener("click", () => {
  modal.style.display = "none";
});

// Optional: Hide the box if user clicks anywhere outside the white box
window.addEventListener("click", (event) => {
  if (event.target === modal) {
    modal.style.display = "none";
  }
});
