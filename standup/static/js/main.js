(function () {
    "use strict";

    // -----------------------
    // SECTION - Spinner
    // -----------------------
    const spinner = () => {
        setTimeout(() => {
            const spinnerElement = document.getElementById("spinner");
            if (spinnerElement) {
                spinnerElement.classList.remove("show");
            }
        }, 1);
    };
    spinner();

    // -----------------------
    // SECTION - Back to top button
    // -----------------------
    window.addEventListener('scroll', function () {
        const backToTopButton = document.querySelector('.back-to-top');
        if (window.scrollY > 300) {
            backToTopButton.style.display = 'block';
            backToTopButton.style.opacity = '1';
        } else {
            backToTopButton.style.opacity = '0';
            setTimeout(() => {
                backToTopButton.style.display = 'none';
            }, 600);  // Matches the fadeOut timing from jQuery
        }
    });

    document.querySelector('.back-to-top').addEventListener('click', function (e) {
        e.preventDefault();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // -----------------------
    // SECTION - Sidebar Toggler
    // -----------------------
    document.querySelector('.sidebar-toggler').addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector('.sidebar').classList.toggle("open");
        document.querySelector('.content').classList.toggle("open");
    });

    // -----------------------
    // SECTION - Calendar
    // -----------------------
    flatpickr("#calender", {
        inline: true,
        dateFormat: "d/m/Y",  // Adjust based on the required format
    });

    // -----------------------
    // SECTION - Completion Node Phrase
    // -----------------------
    const CatchyPhrase = function(type) {
        if (type === "resolve") {
            const completionText = [
                "Item Has Been Resolved - Good Work Team!",
                "Another One Bites The Dust",
                "Done and dusted, Item Busted.",
                "Get your tasks done, like a boss!",
                "Nothing But Net",
            ];
            return completionText[Math.floor(Math.random() * completionText.length)];
        } else if (type === "monitor") {
            const completionText = [
                "And Now Our Watch Begins",
                "We've got our eyes on you",
                "Almost Little One.",
            ];
            return completionText[Math.floor(Math.random() * completionText.length)];
        }
    };

    // -----------------------
    // SECTION - Toast Notification - Resolved
    // -----------------------
    const resolvedToast = Toastify({
        text: CatchyPhrase("resolve"),
        duration: 1100,
        gravity: "bottom",
        position: "center",
        stopOnFocus: true,
        selector: "toast-node",
        style: {
            background: "linear-gradient(to right, #00b09b, #96c93d)",
        },
        callback: function () {
            location.reload();
        },
    });

    // -----------------------
    // SECTION - AJAX Resolve Item
    // -----------------------
    const resolveItem = function(pk) {
        fetch("http://localhost:8000/solve-item", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ pk }),
        })
        .then(() => {
            resolvedToast.showToast();
        });
    };

    // -----------------------
    // SECTION - Toast Notification - Monitoring
    // -----------------------
    const monitorToast = Toastify({
        text: CatchyPhrase("monitor"),
        duration: 33300,
        gravity: "top",
        position: "center",
        stopOnFocus: true,
        selector: "toast-node",
        style: {
            background: "linear-gradient(to right, #0000, #9f00ff)",
        },
        callback: function () {
            location.reload();
        },
    });

    // -----------------------
    // SECTION - AJAX Monitor Item
    // -----------------------
    const moveToMonitoring = function(pk) {
        fetch("http://localhost:8000/convert", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ pk }),
        })
        .then(() => {
            monitorToast.showToast();
            location.reload();
        });
    };

    // -----------------------
    // SECTION - Show All Item Log
    // -----------------------
    const showAllItemsLog = function() {
        const itemLog = document.getElementById("item-log");
        const itemTables = document.querySelectorAll(".item-segmentation");

        if (itemLog.style.display === "none") {
            itemTables.forEach(el => el.style.display = "none");
            itemLog.style.display = "block";
        } else {
            itemLog.style.display = "none";
            itemTables.forEach(el => el.style.display = "block");
        }
    };

    // -----------------------
    // SECTION - AJAX Re-Open Item
    // -----------------------
    const reopenItem = function(pk) {
        fetch("http://localhost:8000/reopen", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ pk }),
        })
        .then(() => {
            monitorToast.showToast();
            location.reload();
        });
    };

    // -----------------------
    // SECTION -  AJAX - Create Item
    // -----------------------
    const createItem = function() {
        const formData = new FormData(document.querySelector("form"));
        fetch("/api/items", {
            method: "POST",
            body: formData,
        })
        .then(() => {
            successfulItemCreation.showToast();
            location.reload();
        });
    };

    // -----------------------
    // SECTION - Bootstrap Modal Handling
    // -----------------------
    const addNewItemModal = new bootstrap.Modal(document.getElementById("add-item-modal"));

    const showAddItemModal = function() {
        addNewItemModal.show();
    };

    const closeAddItemModal = function() {
        addNewItemModal.dispose();
    };

    // -----------------------
    // SECTION - Event Listeners
    // -----------------------
    document.getElementById("add-item-modal").addEventListener("click", showAddItemModal);
    document.getElementById("cancel-add-item").addEventListener("click", showAddItemModal);

})();