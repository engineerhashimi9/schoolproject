document.addEventListener('DOMContentLoaded', () => {
    // ==========================================
    // 1. DOM Elements
    // ==========================================
    const allDaysInput = document.getElementById('all-days-input');
    const hiddenAllDays = document.getElementById('hidden-all-days');
    const table = document.getElementById('attendance-table');
    const searchInput = document.getElementById('search-input');
    const autofillBtn = document.getElementById('autofill-btn');
    const autofillBtnBottom = document.getElementById('autofill-btn-bottom');
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toast-msg');

    const kpiRate = document.getElementById('kpi-rate');
    const kpiBar = document.getElementById('kpi-bar');
    const kpiTotalDays = document.getElementById('kpi-total-days');
    const kpiAbsent = document.getElementById('kpi-absent');

    // ==========================================
    // 2. Feedback Notification Toast
    // ==========================================
    function showToast(message) {
        if (!toast || !toastMsg) return;
        toastMsg.textContent = message;
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3200);
    }

    // ==========================================
    // 3. Calculation Logic
    // ==========================================
    function recalculateRow(row) {
        const allDays = parseInt(allDaysInput ? allDaysInput.value : 24, 10) || 24;
        const presentInput = row.querySelector('.input-present');
        const absentInput = row.querySelector('.input-absent');
        const sickInput = row.querySelector('.input-sick');
        const excusedInput = row.querySelector('.input-excused');

        const pctLabel = row.querySelector('.pct-label');
        const pctBar = row.querySelector('.pct-bar');
        const rowAllDaysLabel = row.querySelector('.row-alldays');

        if (rowAllDaysLabel) rowAllDaysLabel.textContent = allDays;

        const presentDays = parseInt(presentInput ? presentInput.value : 0, 10) || 0;

        const percentage = allDays > 0
            ? Math.min(100, Math.max(0, Math.round((presentDays / allDays) * 1000) / 10))
            : 0;

        if (pctLabel) pctLabel.textContent = percentage + '٪';
        if (pctBar) pctBar.style.width = percentage + '%';

        // Health color coding
        let color = '#dc2626';
        if (percentage >= 85) {
            color = '#059669';
        } else if (percentage >= 70) {
            color = '#d97706';
        }

        if (pctLabel) pctLabel.style.color = color;
        if (pctBar) pctBar.style.backgroundColor = color;
    }

    function recalculateOverallKPIs() {
        if (!table) return;
        const rows = table.querySelectorAll('.student-row');
        const allDays = parseInt(allDaysInput ? allDaysInput.value : 24, 10) || 24;

        let totalPresent = 0;
        let totalAbsent = 0;
        let totalStudents = rows.length;

        rows.forEach(row => {
            const p = parseInt(row.querySelector('.input-present')?.value || 0, 10) || 0;
            const a = parseInt(row.querySelector('.input-absent')?.value || 0, 10) || 0;
            totalPresent += p;
            totalAbsent += a;
        });

        if (kpiAbsent) kpiAbsent.textContent = totalAbsent;

        const maxPossibleDays = totalStudents * allDays;
        const avgPercentage = maxPossibleDays > 0
            ? Math.min(100, Math.max(0, Math.round((totalPresent / maxPossibleDays) * 1000) / 10))
            : 0;

        if (kpiRate) kpiRate.textContent = avgPercentage + '٪';
        if (kpiBar) {
            kpiBar.style.width = avgPercentage + '%';
            kpiBar.style.backgroundColor = avgPercentage >= 85 ? '#059669' : (avgPercentage >= 70 ? '#d97706' : '#dc2626');
        }
    }

    function recalculateAll() {
        if (!table) return;
        const rows = table.querySelectorAll('.student-row');
        rows.forEach(row => recalculateRow(row));
        recalculateOverallKPIs();
    }

    // ==========================================
    // 4. Auto-Fill All Present Handler
    // ==========================================
    function triggerAutofill() {
        const allDays = parseInt(allDaysInput ? allDaysInput.value : 24, 10) || 24;
        if (!table) return;
        const rows = table.querySelectorAll('.student-row');

        rows.forEach(row => {
            const presentInput = row.querySelector('.input-present');
            const absentInput = row.querySelector('.input-absent');
            const sickInput = row.querySelector('.input-sick');
            const excusedInput = row.querySelector('.input-excused');

            if (presentInput) presentInput.value = allDays;
            if (absentInput) absentInput.value = 0;
            if (sickInput) sickInput.value = 0;
            if (excusedInput) excusedInput.value = 0;
            recalculateRow(row);
        });

        recalculateOverallKPIs();
        showToast(`حاضری تمام شاگردان روی ${allDays} روز حاضر تنظیم شد.`);
    }

    if (autofillBtn) autofillBtn.addEventListener('click', triggerAutofill);
    if (autofillBtnBottom) autofillBtnBottom.addEventListener('click', triggerAutofill);

    // ==========================================
    // 5. Total Days Change Event
    // ==========================================
    if (allDaysInput) {
        allDaysInput.addEventListener('input', () => {
            const newTotal = parseInt(allDaysInput.value, 10) || 24;
            if (hiddenAllDays) hiddenAllDays.value = newTotal;
            if (kpiTotalDays) kpiTotalDays.textContent = newTotal;
            recalculateAll();
        });
    }

    // ==========================================
    // 6. Table Number Inputs Delegation
    // ==========================================
    if (table) {
        table.addEventListener('input', (event) => {
            if (event.target.matches('.input-present, .input-absent, .input-sick, .input-excused')) {
                const parentRow = event.target.closest('.student-row');
                if (parentRow) {
                    recalculateRow(parentRow);
                    recalculateOverallKPIs();
                }
            }
        });
    }

    // ==========================================
    // 7. Instant Search Filter
    // ==========================================
    if (searchInput && table) {
        searchInput.addEventListener('input', () => {
            const query = searchInput.value.trim().toLowerCase();
            const rows = table.querySelectorAll('.student-row');

            rows.forEach(row => {
                const name = (row.dataset.name || '').toLowerCase();
                const parent = (row.dataset.parent || '').toLowerCase();
                const code = (row.dataset.code || '').toLowerCase();

                if (name.includes(query) || parent.includes(query) || code.includes(query)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // Initialize calculations on initial page render
    recalculateAll();
});