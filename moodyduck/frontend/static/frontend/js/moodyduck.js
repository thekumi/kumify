document.addEventListener("DOMContentLoaded", () => {
  const body = document.body;
  const sidebar = document.getElementById("md-sidebar");
  const overlay = document.getElementById("md-sidebar-overlay");
  const sidebarToggle = document.querySelector("[data-sidebar-toggle]");
  const scrollTop = document.getElementById("md-scroll-top");

  const closeSidebar = () => body.classList.remove("md-sidebar-open");
  const openSidebar = () => body.classList.add("md-sidebar-open");

  if (sidebar && overlay && sidebarToggle) {
    sidebarToggle.addEventListener("click", () => {
      if (body.classList.contains("md-sidebar-open")) {
        closeSidebar();
      } else {
        openSidebar();
      }
    });

    overlay.addEventListener("click", closeSidebar);

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        closeSidebar();
      }
    });

    window.addEventListener("resize", () => {
      if (window.innerWidth >= 992) {
        closeSidebar();
      }
    });
  }

  if (scrollTop) {
    const syncScrollTopVisibility = () => {
      scrollTop.classList.toggle("is-visible", window.scrollY > 320);
    };

    syncScrollTopVisibility();
    window.addEventListener("scroll", syncScrollTopVisibility, { passive: true });
    scrollTop.addEventListener("click", (event) => {
      event.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }
});
