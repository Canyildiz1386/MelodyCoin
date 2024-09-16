function copyCode(){
    const walletCode = document.getElementById("walletCode").textContent;
    navigator.clipboard.writeText(walletCode)
    .then(()=>{
        const copyMessage = document.getElementById("copyMessage");
        copyMessage.textContent = "Code copied!";
         setTimeout(()=>{copyMessage.textContent=" "},3000);
    })
   .catch(err=>{
    console.error('failed to copy text:', err);})   
   
}