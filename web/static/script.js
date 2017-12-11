window.setTimeout(function() {
    $('.logo').css('animation-duration', '0.5s');
}, 1100);


// COPIED FROM KEVIN POWELL

$('.menu-toggle').click(function() {

  $('.site-nav').toggleClass('site-nav--open', 500);
  $(this).toggleClass('open');

})
