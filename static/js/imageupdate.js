var pictureList = [
    "http://localhost:5000/static/1.JPG",
    "http://localhost:5000/static/2.JPG",
    "http://localhost:5000/static/3.JPG",
    "http://localhost:5000/static/4.JPG",
    "http://localhost:5000/static/5.JPG",
    "http://localhost:5000/static/6.JPG",
    "http://localhost:5000/static/7.JPG",
    "http://localhost:5000/static/8.JPG"];

//Change pcb image depending on colour selected
//
function update_image(){
	
	var pcb_type = document.getElementById('adapter').value;
	
        document.getElementById('pcb_link').href = "static/"+pcb_type+".JPG";
        document.pcb.src = "static/"+pcb_type+".JPG";

}

function update_price(){
    
}
