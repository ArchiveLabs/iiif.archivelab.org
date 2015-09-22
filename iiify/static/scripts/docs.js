$(function() {
    console.log('working');
    $('nav ol li a').click(function(event) {
	alert(event.target);
    });
});
