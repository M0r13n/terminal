function displayErrors(fieldName, errors){
    $(`#${fieldName}`).text(errors[0]);
}
$(document).ready(function () {
    const url = "http://localhost:5000/session/new";
    $("#demographyForm").submit(function (event) {
        event.preventDefault();

        $.ajax({
            url: url,
            type: "POST",
            data: $(this).serialize(),
            dataType: "json",
            success: function (response) {
                const uuid = response.uuid;
                localStorage.setItem('uuid', uuid);
                window.location.href = '/';
            },
            error: function(response) {
                const json = response.responseJSON;
                for (err of json.errors){
                    const fieldName = err[0];
                    const errors = err[1];
                    displayErrors(fieldName, errors);
                }
            }
        });
        return false;
    });
});
