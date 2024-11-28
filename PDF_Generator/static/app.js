document.getElementById("pdf-form").addEventListener("submit", async (e) => {
    e.preventDefault();  // Prevent the form from refreshing the page

    const formData = new FormData();
    formData.append("text", document.getElementById("text").value);
    formData.append("image", document.getElementById("image").files[0]);
    formData.append("template", document.getElementById("template").value);

    try {
        // Make the AJAX request to the backend to generate the PDF
        const response = await fetch("/generate-pdf", {
            method: "POST",
            body: formData,
        });

        // Convert the response to JSON
        const data = await response.json();

        // Check if the response is successful
        if (response.ok) {
            // Show the download button if the PDF was successfully generated
            const downloadContainer = document.getElementById("download-container");
            downloadContainer.innerHTML = `
                <a href="${data.pdf_url}" class="btn btn-success" download>Download PDF</a>
            `;
        } else {
            // Show error if the PDF generation failed
            alert("Error: " + data.error);
        }
    } catch (error) {
        // Handle network or other errors
        console.error("An error occurred:", error);
        alert("An error occurred: " + error.message);
    }
});
