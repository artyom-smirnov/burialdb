$( document ).ready(function() {
    $(".clickable-row").click(function() {
        window.location = $(this).data("href");
    });
});


function activate_pagination(page, load_more_url, list_element) {
    var current_page = page;

    $(window).scroll(function () {
        if ($(window).scrollTop() === $(document).height() - $(window).height()) {
            load_more();
        }
    });

    function load_more() {
        $.ajax({
            url: load_more_url,
            data: {"page": current_page + 1},
            contentType: "application/json",
            success: function (data) {
                current_page += 1;
                list_element.after(data.content);
            },
            error: function () {
                load_more = function () {
                }
            }
        });
    }
}
