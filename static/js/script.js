function toggleSidebar() {
    var sidebar = document.getElementById("sidebar");
    var mainContent = document.getElementById("main-content");
    sidebar.classList.toggle("collapsed");
    mainContent.classList.toggle("expanded");
}
