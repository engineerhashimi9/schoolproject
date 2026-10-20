document.addEventListener('DOMContentLoaded', () => {
    
    // ==========================================
    // 1. Modal Elements
    // ==========================================
    const modal = document.getElementById('paymentModal');
    const openBtn = document.getElementById('openModalBtn');
    const closeBtn = document.getElementById('closeModalBtn');
    const cancelBtn = document.getElementById('cancelModalBtn');

    // ==========================================
    // 2. Modal Functions
    // ==========================================
    function openModal() {
        if (modal) {
            modal.classList.add('show');
            document.body.style.overflow = 'hidden'; // Prevent background scrolling
        }
    }

    function closeModal() {
        if (modal) {
            modal.classList.remove('show');
            document.body.style.overflow = ''; // Restore background scrolling
        }
    }

    // ==========================================
    // 3. Event Listeners
    // ==========================================
    
    // Open modal via Hero button
    if (openBtn) {
        openBtn.addEventListener('click', openModal);
    }

    // Close modal via "X" button or "Cancel" button
    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (cancelBtn) cancelBtn.addEventListener('click', closeModal);

    // Close modal when clicking on the dark overlay background
    if (modal) {
        modal.addEventListener('click', (event) => {
            // Check if the click was exactly on the overlay, not inside the modal content
            if (event.target === modal) {
                closeModal();
            }
        });
    }
});