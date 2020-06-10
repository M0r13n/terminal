$(document).ready(function () {
    const uuid = localStorage.getItem('uuid');
    $("#feedbackForm").submit(function (event) {
        event.preventDefault();
        if (uuid) {
            $.ajax({
                beforeSend: function (request) {
                    request.setRequestHeader("X-UUID", uuid); // uuid header
                },
                url: 'https://api.command-line.online/feedback',
                type: "POST",
                data: $(this).serialize(),
                success: function (result) {
                },
                error: function (xhr, resp, text) {
                    console.log(xhr, resp, text);
                }
            })
        }
        $('#submit').text('Thank You!');
        $('#submit').attr('disabled', true);
        return false;
    });
});
