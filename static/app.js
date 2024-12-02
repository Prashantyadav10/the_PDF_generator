document.addEventListener('DOMContentLoaded', function () {
    // Ensure the script runs after the DOM is fully loaded

    const form = document.getElementById('pdf-form');
    const downloadContainer = document.getElementById('download-container');
    const downloadLink = document.getElementById('download-link');
    const loadingMessage = document.getElementById('loading-message');
    const errorMessage = document.getElementById('error-message'); // New element for error display

    // Reset error message when the form is opened
    errorMessage.style.display = 'none';

    form.addEventListener('submit', function (event) {
        event.preventDefault();  // Prevent form submission

        var formData = new FormData(this);  // Collect form data

        // Reset the error message and show the loading message
        errorMessage.style.display = 'none';
        document.getElementById('download-container').style.display = 'none';
        document.getElementById('loading-message').style.display = 'block';

        // Set up timeout
        const timeout = 5000; // Set timeout to 5 seconds
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        // Make AJAX request to Flask backend to generate the PDF
        fetch('/generate-pdf', {
            method: 'POST',
            body: formData,
            signal: controller.signal
        })
        .then(response => response.json())
        .then(data => {
            clearTimeout(timeoutId); // Clear the timeout if the request succeeds
            loadingMessage.style.display = 'none';  // Hide loading message

            if (data.pdf_url) {
                // Show the download link
                downloadLink.href = data.pdf_url;
                downloadContainer.style.display = 'block';
                form.reset(); // Reset form fields after successful PDF generation
            } else {
                displayError('Error: ' + (data.error || 'An unknown error occurred.'));
            }
        })
        .catch(error => {
            clearTimeout(timeoutId); // Clear the timeout
            loadingMessage.style.display = 'none';  // Hide loading message
            if (error.name === 'AbortError') {
                displayError('Request timed out. Please try again.');
            } else {
                console.error('Error:', error);
                displayError('An error occurred while generating the PDF');
            }
        });
    });

    // Function to display error message
    function displayError(message) {
        errorMessage.innerText = message;
        errorMessage.style.display = 'block';
    }
});
