var circle = document.getElementById("wav1");
            
var radius = 10;

var selected = "None"
document.getElementById("currwav").innerHTML = selected;


function printMousePos(event) {
    /*document.body.textContent =
    "clientX: " + event.clientX +
    " - clientY: " + event.clientY;
    */
    circle.style.top = (event.clientY) + "px";
    circle.style.left = (event.clientX) + "px";

    document.getElementById("textout").innerHTML = event.clientX + "  " + event.clientY;
}

function doRequest() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
           // when the request is completed
           // alert("XMLHTTPRequest sent.")
        }
    };
    xhttp.open("GET", "/data?x=7&y=4", true);
    xhttp.send();
}


document.addEventListener("click", printMousePos);
                