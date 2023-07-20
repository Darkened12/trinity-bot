var animateBaseClass = 'animate__animated';
var fadeInLeftClass = 'animate__fadeInLeft';


window.addEventListener('load', function() {
    let leftContent = document.getElementById('left-content');

    if (window.innerWidth < 992) {
        leftContent.classList.remove(fadeInLeftClass);
        leftContent.classList.remove(animateBaseClass);
    }
});