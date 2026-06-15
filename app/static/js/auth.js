const token = localStorage.getItem("access_token");
if(token){
  document.getElementById("logoutBtn").style.display = "inline-block";
}  


if (!token) {
  // Not logged in → redirect immediately
   window.location.href = "/static/login.html";
}

// ===== LOGOUT FUNCTION =====
function logout() {
  localStorage.removeItem("access_token");
  window.location.href = "/static/login.html";
}
