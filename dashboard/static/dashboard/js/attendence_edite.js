document.addEventListener('DOMContentLoaded', () => {
    
    // ==========================================
    // 1. DOM Elements
    // ==========================================
    const allDaysInput = document.getElementById('all-days-input');
    const table = document.getElementById('attendance-table');
    const searchInput = document.getElementById('search-input');
    const autofillBtn = document.getElementById('autofill-btn');
    const saveDraftBtn = document.getElementById('save-draft-btn');
    const submitConfirmBtn = document.getElementById('submit-confirm-btn');
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toast-msg');

    // ==========================================
    // 2. UI Feedback Functions
    // ==========================================
    function showToast(message) {
        if (!toast) return;
        toastMsg.textContent = message;
        toast.classList.add('show');
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    // ==========================================
    // 3. Core Logic Functions
    // ==========================================
    
    // Calculates attendance percentage for a single row
    function recalculateRow(row) {
        const allDays = parseInt(allDaysInput.value, 10) || 24;
        const presentInput = row.querySelector('.input-present');
        const absentInput = row.querySelector('.input-absent');
        const excusedInput = row.querySelector('.input-excused');
        
        const pctLabel = row.querySelector('.pct-label');
        const pctBar = row.querySelector('.pct-bar');
        const rowAllDaysLabel = row.querySelector('.row-alldays');

        // Update the display for 'Total Days' in this specific row
        if (rowAllDaysLabel) rowAllDaysLabel.textContent = allDays;

        const presentDays = parseInt(presentInput.value, 10) || 0;
        const excusedDays = parseInt(excusedInput.value, 10) || 0;
        
        // Math: (Present / AllDays) * 100
        const percentage = Math.min(100, Math.max(0, Math.round((presentDays / allDays) * 1000) / 10));

        // Update UI
        pctLabel.textContent = percentage + '٪';
        pctBar.style.width = percentage + '%';

        // Apply colors based on health of attendance
        if (percentage >= 90) {
            pctLabel.className = 'pct-label text-secondary font-bold';
            pctBar.className = 'progress-bar bg-secondary pct-bar';
        } else if (percentage >= 75) {
            pctLabel.className = 'pct-label font-bold text-muted';
            pctBar.className = 'progress-bar bg-primary pct-bar';
        } else {
            pctLabel.className = 'pct-label text-error font-bold';
            pctBar.className = 'progress-bar bg-error pct-bar';
        }
    }

    // Loops through all students to recalculate
    function recalculateAllRows() {
        const rows = table.querySelectorAll('.student-row');
        rows.forEach(row => recalculateRow(row));
    }

    // ==========================================
    // 4. Event Listeners
    // ==========================================
    
    // When the global "Total Days" input changes
    if (allDaysInput) {
        allDaysInput.addEventListener('input', () => {
            const newTotal = parseInt(allDaysInput.value, 10) || 24;
            const kpiTotalDays = document.getElementById('kpi-total-days');
            if (kpiTotalDays) kpiTotalDays.textContent = newTotal;
            
            recalculateAllRows();
        });
    }

    // When any number input inside the table changes (Event Delegation)
    if (table) {
        table.addEventListener('input', (event) => {
            if (event.target.matches('.input-present, .input-absent, .input-excused')) {
                const parentRow = event.target.closest('.student-row');
                if (parentRow) recalculateRow(parentRow);
            }
        });
    }

    // Search / Filter functionality
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            const query = searchInput.value.trim().toLowerCase();
            const rows = table.querySelectorAll('.student-row');
            
            rows.forEach(row => {
                const name = (row.dataset.name || '').toLowerCase();
                const parent = (row.dataset.parent || '').toLowerCase();
                const code = (row.dataset.code || '').toLowerCase();
                
                if (name.includes(query) || parent.includes(query) || code.includes(query)) {
                    row.style.display = ''; // Show
                } else {
                    row.style.display = 'none'; // Hide
                }
            });
        });
    }

    // Auto-fill button: Sets all students to perfect attendance
    if (autofillBtn) {
        autofillBtn.addEventListener('click', () => {
            const allDays = parseInt(allDaysInput.value, 10) || 24;
            const rows = table.querySelectorAll('.student-row');
            
            rows.forEach(row => {
                row.querySelector('.input-present').value = allDays;
                row.querySelector('.input-absent').value = 0;
                row.querySelector('.input-excused').value = 0;
                recalculateRow(row);
            });
            showToast(`حاضری تمام شاگردان روی ${allDays} روز تنظیم شد`);
        });
    }

    // Action Buttons
    if (saveDraftBtn) {
        saveDraftBtn.addEventListener('click', () => showToast('پیش‌نویس موقت با موفقیت ذخیره شد'));
    }

    if (submitConfirmBtn) {
        submitConfirmBtn.addEventListener('click', () => showToast('کارنامه حاضری نهایی و ارسال گردید'));
    }

    // Initialize the math on page load
    recalculateAllRows();
});