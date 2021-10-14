// Document Dot Ready
$(document).ready(function() {

    $(".form-control").focus(function() {
        $(this).removeClass('is-invalid');
    });

    $('#update-profile-form').on('submit', function(event){
        event.preventDefault();
        if ($('#save-profile-btn').hasClass('disabled')) { return; }
        var formData = new FormData($(this)[0]);
        $.ajax({
            url: window.location.pathname,
            type: 'POST',
            data: formData,
            beforeSend: function( jqXHR ){
                $('#save-profile-btn').addClass('disabled');
            },
            complete: function(){
                $('#save-profile-btn').removeClass('disabled');
            },
            success: function(data, textStatus, jqXHR){
                console.log('Status: '+jqXHR.status+', Data: '+JSON.stringify(data));
                $("#profile_saved").show();
            },
            error: function(data, textStatus) {
                console.log('Status: '+data.status+', Response: '+data.responseText);
                try {
                    if (data.responseJSON.hasOwnProperty('err_msg')) {
                        alert(data.responseJSON['err_msg'])
                    } else {
                        $($('#update-profile-form').prop('elements')).each(function () {
                            if (data.responseJSON.hasOwnProperty(this.name)) {
                                $('#' + this.name + '-invalid').empty().append(data.responseJSON[this.name]);
                                $(this).addClass('is-invalid');
                            }
                        });
                    }
                }
                catch(error){
                    console.log(error);
                    alert('Fatal Error: ' + error)
                }
            },
            cache: false,
            contentType: false,
            processData: false
        });
        return false;
    });

// Document Dot Ready
} );
