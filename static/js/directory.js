function myFunction() {
    var search = $('#program_search').val();
    window.location.href = '/programs/q=';
        $.ajax({
            success: function () {
                window.location.href = '/programs/q=' + search;
            },
            error: function () {
                Materialize.toast('Search Failed', 2000);
            }
        });
}