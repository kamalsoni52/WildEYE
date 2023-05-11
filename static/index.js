const navbarmob= document.querySelector(".navbar-mobile");
const head = document.querySelector(".header");

const togglenavbar = () =>{
    head.classList.toggle("active")
}
navbarmob.addEventListener('click',() => togglenavbar());