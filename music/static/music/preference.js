(function() {
    'use strict';
    $('.input-file').each(function() {
        var $input = $(this),
        $label = $input.next('.modified-label'),
        labelVal = $label.html();
        $input.on('change', function(element) {
            var fileName = '';
            if (element.target.value) fileName = element.target.value.split('\\').pop();
                fileName ? $label.addClass('has-file').find('.js-fileName').html(fileName) :    $label.removeClass('has-file').html(labelVal);
            });
        });
})();

var custom_select_block = document.querySelectorAll(".custom_select_block");
                    custom_select_block.forEach(parent => {
                        var label = parent.querySelector(".field_select_genres");
                        var select = parent.querySelector(".select_genres");
                        var text = label.innerHTML;

                        function custom_select() {
                            let selectedOptions = select.selectedOptions;
                            label.innerHTML = "";
                            for (let option of selectedOptions) {
                                let button = document.createElement("button");
                                button.type = "button";
                                button.className = "btn_selected";
                                button.textContent = option.innerHTML;
                                button.onclick = _ => {
                                    option.selected = false;
                                    button.remove();
                                    if (!select.selectedOptions.length) label.innerHTML = text
                                };
                                label.append(button);
                            }
                        }
                        $(function() {
                            custom_select();
                            if (this.querySelectorAll('option:checked').length > 5) {
                                Array.apply(null, this.querySelectorAll('option')).forEach(function(e) {
                                    if (!e.selected) {
                                        e.disabled = true;
                                    }
                                });
                            } else {
                                Array.apply(null, this.querySelectorAll('option')).forEach(function(e) {
                                    if (!e.selected) {
                                        e.disabled = false;
                                    }
                                });
                            }
                        });
                        select.addEventListener("click", function(e) {
                            custom_select();
                            if (this.querySelectorAll('option:checked').length > 5) {
                                Array.apply(null, this.querySelectorAll('option')).forEach(function(e) {
                                    if (!e.selected) {
                                        e.disabled = true;
                                    }
                                });
                            } else {
                                Array.apply(null, this.querySelectorAll('option')).forEach(function(e) {
                                    if (!e.selected) {
                                        e.disabled = false;
                                    }
                                });
                            }
                        })
                    })
                    $('select[multiple] option').on('mousedown', function(e) {
                        var $this = $(this),
                            that = this,
                            scroll = that.parentElement.scrollTop;
                        e.preventDefault();
                        $this.prop('selected', !$this.prop('selected'));
                        setTimeout(function() {
                            that.parentElement.scrollTop = scroll;
                        }, 0);
                        return false;
                    });