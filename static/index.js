var circle = document.getElementById("wav1");
            
            var radius = 10;
            
            function printMousePos(event) {
                /*document.body.textContent =
                "clientX: " + event.clientX +
                " - clientY: " + event.clientY;
                */
                circle.style.top = (event.clientY) + "px";
                circle.style.left = (event.clientX) + "px";
                
                document.getElementById("textout").innerHTML = event.clientX + "  " + event.clientY;
            }
            
            
            document.addEventListener("click", printMousePos);
                