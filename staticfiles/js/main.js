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


    // Worldwide Sales Chart
    var ctx1 = $("#worldwide-sales").get(0).getContext("2d");
    var myChart1 = new Chart(ctx1, {
        type: "bar",
        data: {
            labels: ["2016", "2017", "2018", "2019", "2020", "2021", "2022"],
            datasets: [{
                label: "USA",
                data: [15, 30, 55, 65, 60, 80, 95],
                backgroundColor: "rgba(235, 22, 22, .7)"
            },
            {
                label: "UK",
                data: [8, 35, 40, 60, 70, 55, 75],
                backgroundColor: "rgba(235, 22, 22, .5)"
            },
            {
                label: "AU",
                data: [12, 25, 45, 55, 65, 70, 60],
                backgroundColor: "rgba(235, 22, 22, .3)"
            }
            ]
        },
        options: {
            responsive: true
        }
    });


    // Salse & Revenue Chart
    var ctx2 = $("#salse-revenue").get(0).getContext("2d");
    var myChart2 = new Chart(ctx2, {
        type: "line",
        data: {
            labels: ["2016", "2017", "2018", "2019", "2020", "2021", "2022"],
            datasets: [{
                label: "Salse",
                data: [15, 30, 55, 45, 70, 65, 85],
                backgroundColor: "rgba(235, 22, 22, .7)",
                fill: true
            },
            {
                label: "Revenue",
                data: [99, 135, 170, 130, 190, 180, 270],
                backgroundColor: "rgba(235, 22, 22, .5)",
                fill: true
            }
            ]
        },
        options: {
            responsive: true
        }
    });



    // Single Line Chart
    var ctx3 = $("#line-chart").get(0).getContext("2d");
    var myChart3 = new Chart(ctx3, {
        type: "line",
        data: {
            labels: [50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150],
            datasets: [{
                label: "Salse",
                fill: false,
                backgroundColor: "rgba(235, 22, 22, .7)",
                data: [7, 8, 8, 9, 9, 9, 10, 11, 14, 14, 15]
            }]
        },
        options: {
            responsive: true
        }
    });


    // Single Bar Chart
    var ctx4 = $("#bar-chart").get(0).getContext("2d");
    var myChart4 = new Chart(ctx4, {
        type: "bar",
        data: {
            labels: ["Italy", "France", "Spain", "USA", "Argentina"],
            datasets: [{
                backgroundColor: [
                    "rgba(235, 22, 22, .7)",
                    "rgba(235, 22, 22, .6)",
                    "rgba(235, 22, 22, .5)",
                    "rgba(235, 22, 22, .4)",
                    "rgba(235, 22, 22, .3)"
                ],
                data: [55, 49, 44, 24, 15]
            }]
        },
        options: {
            responsive: true
        }
    });


    // Pie Chart
    var ctx5 = $("#pie-chart").get(0).getContext("2d");
    var myChart5 = new Chart(ctx5, {
        type: "pie",
        data: {
            labels: ["Italy", "France", "Spain", "USA", "Argentina"],
            datasets: [{
                backgroundColor: [
                    "rgba(235, 22, 22, .7)",
                    "rgba(235, 22, 22, .6)",
                    "rgba(235, 22, 22, .5)",
                    "rgba(235, 22, 22, .4)",
                    "rgba(235, 22, 22, .3)"
                ],
                data: [55, 49, 44, 24, 15]
            }]
        },
        options: {
            responsive: true
        }
    });


    // Doughnut Chart
    var ctx6 = $("#doughnut-chart").get(0).getContext("2d");
    var myChart6 = new Chart(ctx6, {
        type: "doughnut",
        data: {
            labels: ["Italy", "France", "Spain", "USA", "Argentina"],
            datasets: [{
                backgroundColor: [
                    "rgba(235, 22, 22, .7)",
                    "rgba(235, 22, 22, .6)",
                    "rgba(235, 22, 22, .5)",
                    , "rgba(235, 22, 22, .4)",
                    "rgba(235, 22, 22, .3)"
                ],
                data: [55, 49, 44, 24, 15]
            }]
        },
        options: {
            responsive: true
        }
    });


})(jQuery);

function CatchyPhrase(type) {
    if (type == 'resolve') {
        const completionText = ['Item Has Been Resolved - Good Work Team!', 'Another One Bites The Dust', 'Done and dusted, Item Busted.', 'Get your tasks done, like a boss!', 'Nothing But Net']
        return completionText[Math.floor(Math.random() * completionText.length)]

    } else if (type == 'monitor') {
        const completionText = ['And Now Our Watch Begins', 'We\'ve got our eyes on you', 'Almost Little One.']
        return completionText[Math.floor(Math.random() * completionText.length)]

    }
};


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
var addNewItemModal = new bootstrap.Modal(document.getElementById('add-item-modal'))
// var editItemitemModal = new bootstrap.Modal(document.getElementById('edit-item-modal'))

function showAddItemModal() {
    addNewItemModal.show()
};

function closeAddItemModal() {
    addNewItemModal.dispose()
}
// Event Listensers to open and close the `add item modals`
document.getElementById('add-item-modal').addEventListener('click', showAddItemModal);
document.getElementById('cancel-add-item').addEventListener('click', showAddItemModal);

// var myModal = new bootstrap.Modal(document.getElementById('add-item-modal'))
// document.getElementById("add-item-btn").addEventListener("click", function () {
//     myModal.toggle()
// });

// $.getJSON("https://the-dozens.onrender.com/insult", response => {
//     $("#joke").text(
//         Object.values(response)[0]
//     );
// });
