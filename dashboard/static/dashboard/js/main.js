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

  // 4. Academic Custom Confirmation Modal System
  const confirmOverlay = document.getElementById('confirmModalOverlay');
  const confirmCloseBtn = document.getElementById('confirmModalCloseBtn');
  const confirmCancelBtn = document.getElementById('confirmModalCancelBtn');
  const confirmProceedBtn = document.getElementById('confirmModalProceedBtn');
  const confirmTitle = document.getElementById('confirmModalTitle');
  const confirmMessage = document.getElementById('confirmModalMessage');
  const confirmTargetBox = document.getElementById('confirmModalTargetBox');
  const confirmTargetName = document.getElementById('confirmModalTargetName');

  let activeConfirmCallback = null;

  window.showCustomConfirm = function (options) {
    if (!confirmOverlay) return;

    const title = options.title || 'تأیید غیرفعال‌سازی';
    const message = options.message || 'آیا از انجام این عملیات اطمینان دارید؟';
    const target = options.targetName || '';
    const confirmText = options.confirmText || 'بله، غیرفعال شود';
    const confirmUrl = options.confirmUrl || '#';

    if (confirmTitle) confirmTitle.textContent = title;
    if (confirmMessage) confirmMessage.textContent = message;

    if (confirmTargetBox && confirmTargetName) {
      if (target) {
        confirmTargetName.textContent = target;
        confirmTargetBox.style.display = 'flex';
      } else {
        confirmTargetBox.style.display = 'none';
      }
    }

    if (confirmProceedBtn) {
      confirmProceedBtn.setAttribute('href', confirmUrl);
      confirmProceedBtn.innerHTML = '<i class="fa-solid fa-check"></i> ' + confirmText;
    }

    activeConfirmCallback = typeof options.onConfirm === 'function' ? options.onConfirm : null;

    confirmOverlay.classList.add('active');
    confirmOverlay.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  };

  window.closeCustomConfirm = function () {
    if (!confirmOverlay) return;
    confirmOverlay.classList.remove('active');
    confirmOverlay.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    activeConfirmCallback = null;
  };

  if (confirmCloseBtn) {
    confirmCloseBtn.addEventListener('click', window.closeCustomConfirm);
  }

  if (confirmCancelBtn) {
    confirmCancelBtn.addEventListener('click', window.closeCustomConfirm);
  }

  if (confirmOverlay) {
    confirmOverlay.addEventListener('click', function (e) {
      if (e.target === confirmOverlay) {
        window.closeCustomConfirm();
      }
    });
  }

  if (confirmProceedBtn) {
    confirmProceedBtn.addEventListener('click', function (e) {
      if (activeConfirmCallback) {
        e.preventDefault();
        activeConfirmCallback();
        window.closeCustomConfirm();
      }
    });
  }

  // Handle ESC key to dismiss confirmation modal
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && confirmOverlay && confirmOverlay.classList.contains('active')) {
      window.closeCustomConfirm();
    }
  });

  // Global delegated click handler for all elements with .btn-trigger-confirm or [data-confirm-url]
  document.addEventListener('click', function (e) {
    const trigger = e.target.closest('.btn-trigger-confirm, [data-confirm-url]');
    if (trigger) {
      e.preventDefault();
      e.stopPropagation();

      const url = trigger.getAttribute('data-confirm-url') || trigger.getAttribute('href') || '#';
      const title = trigger.getAttribute('data-confirm-title') || 'تأیید غیرفعال‌سازی';
      const message = trigger.getAttribute('data-confirm-message') || 'آیا از غیرفعال‌سازی این مورد اطمینان دارید؟';
      const targetName = trigger.getAttribute('data-confirm-name') || '';
      const confirmText = trigger.getAttribute('data-confirm-btn') || 'بله، غیرفعال شود';

      window.showCustomConfirm({
        title: title,
        message: message,
        targetName: targetName,
        confirmUrl: url,
        confirmText: confirmText
      });
    }
  });
});
