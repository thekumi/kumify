/* MoodyDuck UI – custom interactions */
(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    // ── Sidebar toggle (mobile) ─────────────────────────────
    const sidebar  = document.getElementById('md-sidebar');
    const overlay  = document.getElementById('md-sidebar-overlay');
    const toggles  = document.querySelectorAll('[data-sidebar-toggle]');

    function openSidebar() {
      sidebar && sidebar.classList.add('open');
      overlay && overlay.classList.add('open');
    }

    function closeSidebar() {
      sidebar && sidebar.classList.remove('open');
      overlay && overlay.classList.remove('open');
    }

    toggles.forEach(function (btn) {
      btn.addEventListener('click', function () {
        sidebar && sidebar.classList.contains('open') ? closeSidebar() : openSidebar();
      });
    });

    overlay && overlay.addEventListener('click', closeSidebar);

    // ── Collapsible nav groups ──────────────────────────────
    document.querySelectorAll('.md-nav-collapse-toggle').forEach(function (toggle) {
      toggle.addEventListener('click', function () {
        const targetId = this.getAttribute('data-target');
        const target   = document.getElementById(targetId);
        if (!target) return;

        const isOpen = target.classList.contains('show');

        // Close all
        document.querySelectorAll('.md-nav-collapse-inner.show').forEach(function (el) {
          el.classList.remove('show');
        });
        document.querySelectorAll('.md-nav-collapse-toggle[aria-expanded="true"]').forEach(function (el) {
          el.setAttribute('aria-expanded', 'false');
        });

        if (!isOpen) {
          target.classList.add('show');
          this.setAttribute('aria-expanded', 'true');
        }
      });
    });

    // ── Scroll-to-top button ────────────────────────────────
    const scrollBtn = document.getElementById('md-scroll-top');
    if (scrollBtn) {
      window.addEventListener('scroll', function () {
        scrollBtn.classList.toggle('visible', window.scrollY > 300);
      });

      scrollBtn.addEventListener('click', function (e) {
        e.preventDefault();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    }
  });
}());
