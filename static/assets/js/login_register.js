const formPopup = document.querySelector(".form-popup");
const hidePopupBtn = formPopup.querySelector(".close-btn");
const signupLoginLink = formPopup.querySelectorAll(".bottom-link a");
const loginHeaderBtn = document.getElementById("login-header-btn");
const registerHeaderBtn = document.getElementById("register-header-btn");

// Close form popup
hidePopupBtn.addEventListener("click", () => {
  formPopup.style.display = "none";
});

// Toggle between login and signup forms
signupLoginLink.forEach((link) => {
  link.addEventListener("click", (e) => {
    e.preventDefault();
    formPopup.classList[link.id === "signup-link" ? "add" : "remove"](
      "show-signup"
    );
  });
});

// Show login form from header button
loginHeaderBtn.addEventListener("click", () => {
  formPopup.style.display = "block";
  formPopup.classList.remove("show-signup");
});

// Show register form from header button
registerHeaderBtn.addEventListener("click", () => {
  formPopup.style.display = "block";
  formPopup.classList.add("show-signup");
});

// Show signup form by default
formPopup.style.display = "block";
formPopup.classList.add("show-signup");
