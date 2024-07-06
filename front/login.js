   
   async function fun(username,password){
    const response = await fetch('http://127.0.0.1:8000/user_login/'+username+"/"+password);
    const data = await response.json();
    if(data.status==true){

        document.getElementById('error').style.opacity=0;
        window.location.href="http://127.0.0.1:5500/front/1stpage.html";
    }else{
        document.getElementById('error').style.opacity = 1;
    }

}

document.getElementById("login-button").addEventListener("click", function(event) {
    event.preventDefault(); // Prevent default form submission

    // Get the input values
    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;
    
    fun(username,password);
});
