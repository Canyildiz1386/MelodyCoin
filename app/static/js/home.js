document.getElementById("butt1").addEventListener("click", function(){
    toggleActive(document.getElementById("selec1"), document.getElementById("selec2"), document.getElementById("selec3"));
    });
    document.getElementById("butt2").addEventListener("click", function(){
        toggleActive(document.getElementById("selec2"), document.getElementById("selec1"), document.getElementById("selec3"));
    });
    document.getElementById("butt3").addEventListener("click", function(){
        toggleActive(document.getElementById("selec3"),document.getElementById("selec2"), document.getElementById("selec1"));
    });
    function toggleActive(activespan, inactiveSpan,inactiveSpan2) {
        activespan.classList.add('active');
        inactiveSpan.classList.remove('active');
        inactiveSpan2.classList.remove('active');
    };


function change(){
    const element=document.getElementById("type");
    if (element.classList.contains("bi-shuffle")){
        element.classList.remove("bi-shuffle");
        element.classList.add("bi-repeat");
    }
    else if (element.classList.contains("bi-repeat")){
        element.classList.remove("bi-repeat");
        element.classList.add("bi-repeat-1");
    }
    else if(element.classList.contains("bi-repeat-1")){
        element.classList.remove("bi-repeat-1");
        element.classList.add("bi-shuffle");
    }
    console.log(element.classList);
}
function heart(){
    const element=document.getElementById("heart");
    if (element.classList.contains("bi-heart")){
        element.classList.remove("bi-heart");
        element.classList.add("bi-heart-fill");
    }
    else if (element.classList.contains("bi-heart-fill")){
        element.classList.remove("bi-heart-fill");
        element.classList.add("bi-heart");
    }
}
function play(){
    const element=document.getElementById("play");
    if (element.classList.contains("bi-play-fill")){
        element.classList.remove("bi-play-fill");
        element.classList.add("bi-pause-fill");
    }
    else if (element.classList.contains("bi-pause-fill")){
        element.classList.remove("bi-pause-fill");
        element.classList.add("bi-play-fill");
    } 
}