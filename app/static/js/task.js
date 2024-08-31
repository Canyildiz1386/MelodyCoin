document.getElementById("butt1").addEventListener("click", function(){
toggleActive(document.getElementById("selec1"), document.getElementById("selec2"));
});
document.getElementById("butt2").addEventListener("click", function(){
    toggleActive(document.getElementById("selec2"), document.getElementById("selec1"));
});
function toggleActive(activespan, inactiveSpan) {
    activespan.classList.add('active');
    inactiveSpan.classList.remove('active');
};