document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('research-form');
    const submitBtn = document.getElementById('submit-btn');
    const loadingScreen = document.getElementById('loading-screen');

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const description = document.getElementById('description').value.trim();
        if (!description) {
            alert('Please enter a study description');
            return;
        }

        // Show loading screen
        loadingScreen.style.display = 'flex';
        submitBtn.disabled = true;
        submitBtn.textContent = 'Searching...';

        // Create form data
        const formData = new FormData();
        formData.append('description', description);

        // Send AJAX request
        fetch('study/submit', {
            method: 'POST',
            body: formData
        })
            .then(response => {
                if (response.status === 401) {
                    // Authentication required, redirect to login
                    window.location.href = '/login';
                    return;
                }
                return response.json();
            })
            .then(data => {
                // Hide loading screen
                loadingScreen.style.display = 'none';
                submitBtn.disabled = false;
                submitBtn.textContent = 'Find Participants';

                if (data && data.success) {
                    // Redirect to results page
                    window.location.href = data.redirect;
                } else if (data) {
                    showError(data.error || 'An error occurred while searching for participants');
                }
            })
            .catch(error => {
                // Hide loading screen
                loadingScreen.style.display = 'none';
                submitBtn.disabled = false;
                submitBtn.textContent = 'Find Participants';

                console.error('Error:', error);
                showError('An error occurred while searching for participants');
            });
    });

    function showError(message) {
        // Remove any existing error messages
        const existingError = document.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }

        // Create and display error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;

        const formContainer = document.getElementById('form-container');
        formContainer.appendChild(errorDiv);

        // Scroll to error message
        errorDiv.scrollIntoView({ behavior: 'smooth' });
    }
}); 