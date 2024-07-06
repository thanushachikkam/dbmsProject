async function crossCheck(){
    var userInput = document.getElementById("captcha-input").value;
    var firstname = document.getElementById("first_name").value;
    var lastname = document.getElementById("last_name").value;
    var mail = document.getElementById("mail").value;
    var password = document.getElementById("password").value;
    var passwordNew = document.getElementById("new_password").value;
    return fun(firstname,lastname,mail,password,passwordNew)
}

async function fun(firstname,lastname,mail,password,passwordNew){
    if(password===passwordNew){
        console.log("cs");
    const response = await fetch('http://127.0.0.1:8000/user_signup/'+firstname+"/"+lastname+"/"+mail+"/"+password);
    const data = await response.json();
    if(data.status){
        document.getElementById('error').innerText = "";
        return true;
    }else{
        document.getElementById('error').innerText = data.message;
        console.log("cf");
        return false;
    }
    }else{
        console.log("fw");
        return false;
    }

}

// Function to generate a random CAPTCHA string
var captchaText = '';
function generateCaptcha() {

    var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

    // Length of the CAPTCHA string
    var length = 6;

    // Generate random characters

    var captchaText_new='';
    for (var i = 0; i < length; i++) {
        captchaText_new += characters.charAt(Math.floor(Math.random() * characters.length));

    }
    captchaText=captchaText_new;
    

    // Display the CAPTCHA text
    document.getElementById("captchaDisplay").textContent = captchaText;
}

// Function to verify CAPTCHA
async function verifyCaptcha() {
    
    var userInput = document.getElementById("captcha-input").value;
    var ve=await crossCheck();
    console.log(ve);
    console.log("fr");
    if (userInput === captchaText&&ve) {
        Swal.fire({
            icon: 'success',
            title: 'Login successful!',
            showConfirmButton: false,
            timer: 3000,
            willClose: () => {
                // Redirect to another page upon successful verification after the success message is displayed
                window.location.href = "exp.html";
           }
            
        });
        // You can redirect to another page or perform other actions upon successful verification
    } else {
        Swal.fire({
            icon: 'error',
            title: 'Invalid CAPTCHA',
            text: 'Please try again.',
            timer:3000
        });
    }
}

// Generate CAPTCHA when the page loads
generateCaptcha();
