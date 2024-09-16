// Script to handle modal opening and closing
function openModal(button) {
   
            // Get the modal
            const modal = document.getElementById('nft-modal');

            // Get the card that contains the button
            const card = button.parentElement;
            const nft=card.parentElement;

            // Extract data from the card
            const name = nft.querySelector('.nftName').textContent;
            const description = nft.querySelector('.description').textContent;
            const profit = nft.querySelector('.pro').textContent;
            const coin = nft.querySelector('.nftCoin').textContent;

            // Insert data into modal
            document.getElementById('modal-name').textContent =name;
            document.getElementById('description').textContent =description;
            document.getElementById('profit').textContent = profit;
            document.getElementById('coin').textContent = coin;

            // Show the modal
            modal.style.display = 'block';







}

function closeModalname() {
    document.getElementById("nft-modal").style.display = "none";
}
var modal = document.getElementById("nft-modal");
// Optional: Close modal when clicking outside of it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display="none";
    }
}



