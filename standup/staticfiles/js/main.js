(function ($) {
    "use strict";

    // Spinner
    var spinner = function () {
        setTimeout(function () {
            if ($('#spinner').length > 0) {
                $('#spinner').removeClass('show');
            }
        }, 1);
    };
    spinner();


    // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });
    $('.back-to-top').click(function () {
        $('html, body').animate({ scrollTop: 0 }, 1500, 'easeInOutExpo');
        return false;
    });


    // Sidebar Toggler
    $('.sidebar-toggler').click(function () {
        $('.sidebar, .content').toggleClass("open");
        return false;
    });


    // Progress Bar
    $('.pg-bar').waypoint(function () {
        $('.progress .progress-bar').each(function () {
            $(this).css("width", $(this).attr("aria-valuenow") + '%');
        });
    }, { offset: '80%' });


    // Calender
    $('#calender').datetimepicker({
        inline: true,
        format: 'L'
    });


    // Testimonials carousel
    $(".testimonial-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        items: 1,
        dots: true,
        loop: true,
        nav: false
    });


    // Chart Global Color
    Chart.defaults.color = "#6C7293";
    Chart.defaults.borderColor = "#000000";


    /
    });


function CatchyPhrase(type) {
    if (type == 'resolve') {
        const completionText = ['Item Has Been Resolved - Good Work Team!', 'Another One Bites The Dust', 'Done and dusted, Item Busted.', 'Get your tasks done, like a boss!', 'Nothing But Net']
        return completionText[Math.floor(Math.random() * completionText.length)]

    } else if (type == 'monitor') {
        const completionText = ['And Now Our Watch Begins', 'We\'ve got our eyes on you', 'Almost Little One.']
        return completionText[Math.floor(Math.random() * completionText.length)]

    }
};
// const resolvedToast = Toastify({
//     text: CatchyPhrase('resolve'),
//     duration: 1100,//
//     gravity: "bottom", // `top` or `bottom`
//     position: "center", // `left`, `center` or `right`
//     stopOnFocus: true, // Prevents dismissing of toast on hover
//     selector: "toast-node",
//     style: {
//         background: "linear-gradient(to right, #00b09b, #96c93d)",
//     },       \\\\\\\\\\\\\\\\\\\\\\\\\   A
//     callback: function () {
//         location.reload()AÀAÀ
//     }

// });

function showAllItemsLog() {
    const itemLog = document.getElementById('item-log')

    if (itemLog.style.display == 'none') {
        const itemTables = document.querySelectorAll('.item-segmentation')
        itemTables.forEach(el => el.style.display = "none");
        itemLog.style.display = 'block'
    } else if (itemLog.style.display == 'block') {
        itemLog.style.display = 'none'
        itemTables.style.display = 'block'
    }
}
function resolveItem(pk) {
    $.post({
        url: "http://localhost:8000/solve-item", data: { "pk": pk },
        success: function () {
            resolvedToast.showToast()

        }
    })
}

function moveToMonitoring(pk) {
    $.post({
        url: "http://localhost:8000/convert", data: { "pk": pk },
        success: function () {
            monitorToast.showToast()
            location.reload()
        }
    })
}

function reopenItem(pk) {
    $.post({
        url: "http://localhost:8000/reopen", data: { "pk": pk },
        success: function () {
            monitorToast.showToast()
            location.reload()
        }
    })
};
// Hook to submit the form data from the add ite
function CreateItem() {
    var formData = new FormData(document.querySelector('form'))
    $.post({
        url: "/api/items",
        data: formData,
        success: function () {
            successfulItemCreation.showToast()
            location.reload()
        }

    })
}
// Inititialize Item Modals (Edit and New)
// var editItemitemModal = new bootstrap.Modal(document.getElementById('edit-item-modal'))

// Event Listensers to open and close the `add item modals`

// var myModal = new bootstrap.Modal(document.getElementById('add-item-modal'))
// document.getElementById("add-item-btn").addEventListener("click", function () {
//     myModal.toggle()
// });

// $.getJSON("https://the-dozens.onrender.com/insult", response => {
//     $("#joke").text(
//         Object.values(response)[0]
//     );
// });
