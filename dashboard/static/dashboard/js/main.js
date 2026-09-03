const closeBtn = document.getElementById("closeBoxBtn");
const modal = document.getElementById("msgBoxModal");

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
function disevent(id) {
  modal.innerHTML = `
      <div class="message-content"><h3>اخطار</h3>
      <p class="message">این دانش آموز غیر فعال شود؟</p>
      <a href="http://localhost:8000/dashboard/student/${id}/disable" class="option-btn" >بله</a>
      <button class="option-btn" id="closeBoxBtn">خیر</button></div>`;
  modal.style.display = "flex";
}
