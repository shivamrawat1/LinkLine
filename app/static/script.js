document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('research-form');
    const submitBtn = document.getElementById('submit-btn');
    const loadingScreen = document.getElementById('loading-screen');
    const resultsContainer = document.getElementById('results-container');
    const searchCriteriaDiv = document.getElementById('search-criteria');
    const participantsListDiv = document.getElementById('participants-list');

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
        fetch('/submit', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                // Hide loading screen
                loadingScreen.style.display = 'none';
                submitBtn.disabled = false;
                submitBtn.textContent = 'Find Participants';

                if (data.success) {
                    displayResults(data.results);
                } else {
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

    function displayResults(results) {
        // Display search criteria
        const criteria = results.search_criteria;
        searchCriteriaDiv.innerHTML = `
            <div class="search-criteria">
                <div class="criteria-title">Search Criteria Used:</div>
                <div><strong>Search Query:</strong> ${criteria.search_query}</div>
                <div><strong>Target Roles:</strong> ${criteria.target_roles.join(', ')}</div>
                <div><strong>Target Industries:</strong> ${criteria.target_industries.join(', ')}</div>
                <div><strong>Inclusion Criteria:</strong> ${criteria.inclusion_criteria.join(', ')}</div>
                ${criteria.exclusion_criteria.length > 0 ? `<div><strong>Exclusion Criteria:</strong> ${criteria.exclusion_criteria.join(', ')}</div>` : ''}
            </div>
        `;

        // Display participants
        const participants = results.participants;
        let participantsHTML = `<h3>Found ${participants.length} Potential Participants</h3>`;

        participants.forEach((participant, index) => {
            participantsHTML += `
                <div class="participant-card">
                    <div class="participant-name">${participant.name}</div>
                    <div class="participant-info">
                        <strong>Email:</strong> 
                        ${participant.email !== 'Not found' ?
                    `<a href="mailto:${participant.email}" class="participant-email">${participant.email}</a>` :
                    'Not found'}
                    </div>
                    <div class="participant-info">
                        <strong>LinkedIn:</strong> 
                        ${participant.linkedin_id !== 'Not found' ?
                    `<a href="https://linkedin.com/in/${participant.linkedin_id}" target="_blank">linkedin.com/in/${participant.linkedin_id}</a>` :
                    'Not found'}
                    </div>
                    <div class="participant-info">
                        <strong>Title:</strong> ${participant.title}
                    </div>
                    <div class="participant-info">
                        <strong>Snippet:</strong> ${participant.snippet}
                    </div>
                    <div class="participant-info">
                        <strong>Source:</strong> <a href="${participant.url}" target="_blank">${participant.url}</a>
                    </div>
                </div>
            `;
        });

        participantsListDiv.innerHTML = participantsHTML;
        resultsContainer.style.display = 'block';

        // Scroll to results
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }

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
