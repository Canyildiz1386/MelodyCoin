function copyCode(){
    const link = document.getElementById("invitLink").textContent;
    
    // Check if the clipboard API is supported
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(link)
        .then(() => {
            const copyMessage = document.getElementById("copyMessage");
            copyMessage.textContent = "Link copied!";
            setTimeout(() => { copyMessage.textContent = ""; }, 3000);
        })
        .catch(err => {
            console.error('Failed to copy text:', err);
        });
    } else {
        // Fallback for older browsers
        console.error('Clipboard API not supported');
        const copyMessage = document.getElementById("copyMessage");
        copyMessage.textContent = "Clipboard copy not supported in this browser.";
        setTimeout(() => { copyMessage.textContent = ""; }, 3000);
    }
}
