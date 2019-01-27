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
                $('[data-toggle="tooltip"]').tooltip();
                $('[data-toggle="popover"]').popover();
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
        $('.hide-if-treated').removeClass('d-none');
        $('.hide-if-mia').removeClass('d-none');
        $('.hide-if-killed').removeClass('d-none');
        $('.hide-if-deadinroad').removeClass('d-none');
        $('.hide-if-deadincaptivity').removeClass('d-none');

        switch (parseInt(state.val())) {
            case 0: // website.models.TREATED
                $('.hide-if-treated').addClass('d-none');
                break;
            case 1: // website.models.MIA
                $('.hide-if-mia').addClass('d-none');
                break;
            case 2: // website.models.KILLED
                $('.hide-if-killed').addClass('d-none');
                break;
            case 3: // website.models.DEADINROAD
                $('.hide-if-deadinroad').addClass('d-none');
                break;
            case 4: // website.models.DEADINCAPTIVITY
                $('.hide-if-deadincaptivity').addClass('d-none');
                break;
        }
    }
}
