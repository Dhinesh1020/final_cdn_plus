// scripts.js

$(document).ready(function() {
    // Define additional options for each menu item
    var optionsForHome = [
        { text: 'Section 1', url: '{% url "dns" %}' },
        { text: 'Section 2', url: '{% url "distribution" %}' }
    ];

    // Add click event for menu items with submenu
    $('.has-submenu').click(function(e) {
        e.preventDefault();

        // Clear existing submenu options
        $(this).find('.submenu').empty();

        // Add new submenu options dynamically
        var options = $(this).is('.home') ? optionsForHome : [];
        options.forEach(function(option) {
            $(this).find('.submenu').append('<li><a href="' + option.url + '">' + option.text + '</a></li>');
        }.bind(this));

        // Show/hide submenu
        $(this).find('.submenu').toggle();
    });
});


function highlightCountry() {
    const markers = document.querySelectorAll('.marker');

    markers.forEach(marker => {
        marker.style.backgroundColor = 'red';
    });
}


function openForm(formName) {
    // Hide all forms
    const forms = document.querySelectorAll('.form');
    forms.forEach(form => {
        form.style.display = 'none';
    });

    // Show the selected form
    const selectedForm = document.getElementById(formName);
    if (selectedForm) {
        selectedForm.style.display = 'block';
    }
}