function handleRequest(action, button) {
    // Disable both buttons once one is clicked
    const buttons = button.closest('td').querySelectorAll('button');
    buttons.forEach(btn => btn.disabled = true);

    // Change the button color based on the action
    if (action === 'accept') {
        button.classList.remove('pending');
        button.classList.add('accepted');
        button.innerText = 'Accepted';
        button.style.color = 'green';  // Set text color for accepted state
    } else if (action === 'reject') {
        button.classList.remove('pending');
        button.classList.add('rejected');
        button.innerText = 'Rejected';
        button.style.color = 'red';  // Set text color for rejected state
    }
}


function confirmDelete() {
    document.getElementById('deleteConfirmationPopup').style.display = 'flex';
}

function closePopup() {
    document.getElementById('deleteConfirmationPopup').style.display = 'none';
}

function deleteProvider() {
    // Handle provider deletion logic here
    alert('Provider has been deleted.');
    closePopup(); // Close the popup after deletion
}
