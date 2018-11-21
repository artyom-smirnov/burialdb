$( document ).ready(function() {
    clickable_rows();
    check_state();

    $("#id_state").change(function() {
        check_state();
    });
});

function clickable_rows()
{
    $(".clickable-row").click(function() {
        if ($(this).data("target") === "_blank")
            window.open($(this).data("href"), "_blank");
        else
            window.location = $(this).data("href");
    });
}

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
                $('#' + list_element + ' tr:last').after(data.content);
                clickable_rows();
            },
            error: function () {
                load_more = function () {
                }
            }
        });
    }
}

function copy_data(from, to)
{
    f_elem = $('#'+from);
    t_elem = $('#'+to);
    t_elem.val(f_elem.val());
}

function reset_search() {
    window.location = location.protocol + '//' + location.host + location.pathname;
}

function check_state() {
    var state = $('#id_state');
    if (state)
    {
        switch (parseInt(state.val())) {
            case 1:
                $('.hide-if-killed').removeClass('d-none');
                $('.hide-if-mia').addClass('d-none');
                break;
            case 2:
                $('.hide-if-mia').removeClass('d-none');
                $('.hide-if-killed').addClass('d-none');
                break;
            default:
                $('.hide-if-killed').removeClass('d-none');
                $('.hide-if-mia').removeClass('d-none');
                break;
        }
    }
}
