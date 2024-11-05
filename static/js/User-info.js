const modal = document.getElementById("profileModal");
const editProfileBtn = document.getElementById("editProfileBtn");
const closeBtn = document.getElementById("closeBtn");

// When the user clicks the "Edit Profile" button, open the modal
editProfileBtn.onclick = function() {
    modal.style.display = "block";
}

// When the user clicks the close button (x), close the modal
closeBtn.onclick = function() {
    modal.style.display = "none";
}

// When the user clicks anywhere outside the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

// Optional: Handle form submission (e.g., send data to a server or display a message)
const profileForm = document.getElementById("profileForm");

profileForm.onsubmit = function(event) {
    event.preventDefault(); // Prevent form from refreshing the page

    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const bio = document.getElementById("bio").value;

    console.log("Profile Updated:", { name, email, bio });

    // Close the modal after saving
    modal.style.display = "none";

    // Optionally: Show a success message or send data to a backend
    alert("Profile updated successfully!");
}