// Function to show the toast message
function showToast(message, category) {
    const toast = document.getElementById("toast");
    
    // Set message text
    toast.textContent = message;

    // Add the appropriate class for the message type (success, error)
    toast.className = "toast " + category;
    
    // Add the "show" class to make it visible
    toast.classList.add("show");

    // Remove the toast after 3 seconds
    setTimeout(function () {
        toast.classList.remove("show");
    }, 5000); // Toast will disappear after 3 seconds
}

// Show the toast notification on page load if flash messages exist
document.addEventListener("DOMContentLoaded", function () {
    // Get the flash messages passed from Flask
    const flashMessages = JSON.parse(document.getElementById("flash-messages-data").textContent);
    
    // Display each flash message as a toast
    flashMessages.forEach(function([category, message]) {
        showToast(message, category);
    });
});
