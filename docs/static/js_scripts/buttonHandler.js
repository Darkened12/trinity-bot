var leftContent = document.getElementById('left-content');
var rightContent = document.getElementById('right-content');

var btnBig = document.getElementById('btnBig');


btnBig.addEventListener('click', function() {
    leftContent.classList.remove(fadeInLeftClass);
    leftContent.classList.add('animate__fadeOutLeft');

    rightContent.classList.remove('animate__fadeInRight');
    rightContent.classList.add('animate__fadeOutRight');
});

