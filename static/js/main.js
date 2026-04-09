/* ==========================================================================
   Library Management System - JavaScript
   Author: Ahmed Yousif
   ========================================================================== */

// --- Mobile Navigation Toggle ---
function toggleMenu() {
    const navLinks = document.getElementById('navLinks');
    const navUser = document.getElementById('navUser');
    
    if (navLinks) {
        navLinks.classList.toggle('active');
    }
    if (navUser) {
        navUser.classList.toggle('active');
    }
}

// --- Image Upload Preview ---
// This function runs when a user selects an image file in the add/edit book forms
function previewImage(input) {
    const previewDiv = document.getElementById('image-preview');
    
    // Clear previous preview
    previewDiv.innerHTML = '';
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            // Create a new image element
            const img = document.createElement('img');
            img.src = e.target.result;
            img.alt = 'Book Cover Preview';
            
            // Add a small label
            const label = document.createElement('p');
            label.textContent = 'Preview:';
            label.style.fontSize = '0.85rem';
            label.style.color = 'var(--text-muted)';
            
            // Append to the preview div
            previewDiv.appendChild(label);
            previewDiv.appendChild(img);
        };
        
        // Read the image file as a data URL
        reader.readAsDataURL(input.files[0]);
    }
}

// --- Auto-hide Flash Messages ---
// This automatically hides success/error messages after 4 seconds
document.addEventListener('DOMContentLoaded', () => {
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach(msg => {
        // If it's a danger/error message, don't auto-hide it (let user read it)
        if (!msg.classList.contains('flash-danger')) {
            setTimeout(() => {
                // Fade out effect
                msg.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                msg.style.opacity = '0';
                msg.style.transform = 'translateY(-10px)';
                
                // Remove from DOM after fade out completes
                setTimeout(() => {
                    if (msg.parentElement) {
                        msg.remove();
                    }
                }, 500);
            }, 4000); // 4 seconds delay
        }
    });
});
