function fun() {  
     alert (" Hello Contact us on  \n +91@@@@@@@@@@@  \n Support@gmail.com ");  
}  
  
const signUp = document.querySelector("#signUp");
const signIn = document.querySelector("#signIn");
const passwordIcon = document.querySelectorAll('.password__icon')
const authPassword = document.querySelectorAll('.auth__password')

// when click sign up button
signUp.addEventListener('click', () => {
    document.querySelector('.login__form').classList.remove('active')
    document.querySelector('.register__form').classList.add('active')
    document.querySelector('.ball').classList.add('register')
    document.querySelector('.ball').classList.remove('login')
});

// when click sign in button
signIn.addEventListener('click', () => {
    document.querySelector('.login__form').classList.add('active')
    document.querySelector('.register__form').classList.remove('active')
    document.querySelector('.ball').classList.add('login')
    document.querySelector('.ball').classList.remove('register')
});

// change hidden password to visible password
for (var i = 0; i < passwordIcon.length; ++i) {
    passwordIcon[i].addEventListener('click', (i) => {
        const lastArray = i.target.classList.length - 1
        if (i.target.classList[lastArray] == 'bi-eye-slash') {
            i.target.classList.remove('bi-eye-slash')
            i.target.classList.add('bi-eye')
            i.currentTarget.parentNode.querySelector('input').type = 'text'
        } else {
            i.target.classList.add('bi-eye-slash')
            i.target.classList.remove('bi-eye')
            i.currentTarget.parentNode.querySelector('input').type = 'password'
        }
    });
}
// publish

//declearing html elements

const imgDiv = document.querySelector('.profile-pics');
const img = document.querySelector('#photo');
const file = document.querySelector('#file');
const uploadBtn = document.querySelector('#uploadBtn');

//if user hover on img div 

// imgDiv.addEventListener('mouseenter', function(){
//     uploadBtn.style.display = "";
// });

// //if we hover out from img div

// imgDiv.addEventListener('mouseleave', function(){
//     uploadBtn.style.display = "none";
// });

//lets work for image showing functionality when we choose an image to upload

//when we choose a foto to upload

file.addEventListener('change', function(){
    //this refers to file
    const choosedFile = this.files[0];

    if (choosedFile) {

        const reader = new FileReader(); //FileReader is a predefined function of JS
        reader.addEventListener('load', function(){
            img.setAttribute('src', reader.result);
        });

        reader.readAsDataURL(choosedFile);

   
    }
});