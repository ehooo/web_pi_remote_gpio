function hide_all(pin) {
            $('#led_' + pin).parent('.custom-control').hide();
            $('#pull_up_' + pin).parent('.custom-control').hide();
            $('#pin_' + pin + '_value').hide();
            $('#read_' + pin).hide();
        }

function show_led(pin) {
    $('#led_' + pin).parent('.custom-control').show();
}
function show_button(pin) {
    $('#pull_up_' + pin).parent('.custom-control').show();
    $('#pin_' + pin + '_value').show();
    $('#read_' + pin).show();
}
function show_all(pin) {
    show_led(pin);
    show_button(pin);
}

function check_pin(pin) {
    $.ajax('/' + pin + '/info/', {
        'beforeSend': function (){
            hide_all(pin);
        },
        'success': function(data) {
            if(data.errors.length) return;
            if(data.data.mode == null) {
                $('#pull_up_' + pin).prop('indeterminate', true);
                show_all(data.pin);
            } else if(data.data.mode === 'output') {
                show_led(data.pin);
                if(data.data.value) {
                    $('#led_' + data.pin).attr('checked', 'checked');
                } else {
                    $('#led_' + data.pin).removeAttr('checked');
                }
            } else if(data.data.mode === 'input') {
                $('#pull_up_' + pin).prop('indeterminate', false);
                if (data.data.pull_up) {
                    $('#pull_up_' + data.pin).attr('checked', 'checked');
                } else {
                    $('#pull_up_' + data.pin).removeAttr('checked');
                }
                $('#pull_up_' + data.pin).attr('disabled', 'disabled');
                show_button(data.pin);
            }
        },
    });
}
function led_change(pin, on) {
    let action = 'on';
    if (!on) {
        action = 'off';
    }
    $.ajax('/' + pin + '/' + action + '/', {
        'beforeSend': function (){
            $('#led_' + pin).attr('disabled', 'disabled');
        },
        'success': function() {
            check_pin(pin);
        },
        'complete': function () {
            $('#led_' + pin).removeAttr('disabled');
        }
    });
}

function just_read(pin) {
    $.ajax('/' + pin + '/read/', {
        'success': function(data) {
            $('#pin_' + data.pin + '_value').val(data.data.value);
            check_pin(data.pin);
        },
    });
}
function read(pin) {
    let pull_up = $('#pull_up_' + pin);
    if (pull_up.prop('disabled')) {
        just_read(pin)
        return;
    }
    let up = pull_up.prop('checked');
    let action = 'pull_up';
    if (!up) {
        action = 'pull_down';
    }
    $.ajax('/' + pin + '/' + action + '/', {
        'beforeSend': function (){
            $('#pull_up_' + pin).attr('disabled', 'disabled');
            $('#read_' + pin).attr('disabled', 'disabled');
        },
        'success': function(data) {
            just_read(data.pin);
        },
        'complete': function () {
            $('#read_' + pin).removeAttr('disabled');
        }
    });
}
