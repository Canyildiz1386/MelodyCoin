function copyCode(){
    const link = document.getElementById("invitLink").textContent;
    navigator.clipboard.writeText(link)
    .then(()=>{
        const copyMessage = document.getElementById("copyMessage");
        copyMessage.textContent = "Link copied!";
         setTimeout(()=>{copyMessage.textContent=" "},3000);
    })
   .catch(err=>{
    console.error('failed to copy text:', err);})   
   
}