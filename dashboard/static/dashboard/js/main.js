/**
 * Antigravity Academic School Management System
 * Global Responsive UI & Navigation Controller
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Mobile Sidebar Navigation Drawer
  const mobileToggleBtn = document.getElementById('mobile-toggle-btn');
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  const sidebarCloseBtn = document.getElementById('sidebar-close-btn');

  function openSidebar() {
    if (sidebar) sidebar.classList.add('mobile-open');
    if (overlay) overlay.classList.add('active');
    document.body.classList.add('drawer-open');
  }

  function closeSidebar() {
    if (sidebar) sidebar.classList.remove('mobile-open');
    if (overlay) overlay.classList.remove('active');
    document.body.classList.remove('drawer-open');
  }

  if (mobileToggleBtn) {
    mobileToggleBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      openSidebar();
    });
  }

  if (overlay) {
    overlay.addEventListener('click', closeSidebar);
  }

  if (sidebarCloseBtn) {
    sidebarCloseBtn.addEventListener('click', closeSidebar);
  }

  // Close sidebar on ESC key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && sidebar && sidebar.classList.contains('mobile-open')) {
      closeSidebar();
    }
  });

  // 2. Responsive Table Auto-Enhancement
  // Wrap any table with .table-responsive if not already wrapped
  const tables = document.querySelectorAll('.table-section > table, .card > table, table.data-table, table.attendance-table');
  tables.forEach(function (table) {
    if (!table.closest('.table-responsive')) {
      const wrapper = document.createElement('div');
      wrapper.className = 'table-responsive';
      table.parentNode.insertBefore(wrapper, table);
      wrapper.appendChild(table);
    }
  });

  // 3. Auto-hide messages after 6 seconds
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      if (alert && alert.parentElement) {
        alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        setTimeout(function () {
          if (alert.parentElement) alert.remove();
        }, 400);
      }
    }, 6000);
  });
});
