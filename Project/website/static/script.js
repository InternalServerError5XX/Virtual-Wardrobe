$(function () {
  $('#callback-button').click(function () {
    $('.modal').addClass('modal_active');
    $('body').addClass('hidden');
  });
 
  $('.modal').mouseup(function (e) {
    let modalContent = $(".modal__content");
    if (!modalContent.is(e.target) && modalContent.has(e.target).length === 0) {
      $(this).removeClass('modal_active');
      $('body').removeClass('hidden');
    }
  });
});

$(function () {
  $('#callback-button').click(function () {
    $('.flash_mes').addClass('modal_active');
    $('body').addClass('hidden');
  });

  $('.flash_mes').mouseup(function (e) {
    let modalContent = $(".modal__content");
    if (!modalContent.is(e.target) && modalContent.has(e.target).length === 0) {
      $(this).removeClass('modal_active');
      $('body').removeClass('hidden');
    }
  });
});

$(function () {
  $('#callback-button').click(function () {
    $('.flash_mes_suc').addClass('modal_active');
    $('body').addClass('hidden');
  });

  $('.flash_mes_suc').mouseup(function (e) {
    let modalContent = $(".modal__content");
    if (!modalContent.is(e.target) && modalContent.has(e.target).length === 0) {
      $(this).removeClass('modal_active');
      $('body').removeClass('hidden');
    }
  });
});

$(function() {
    var imagesPreview = function(input, placeToInsertImagePreview) {

        if (input.files) {
            var filesAmount = input.files.length;

            for (i = 0; i < filesAmount; i++) {
                var reader = new FileReader();

                reader.onload = function(event) {
                    $($.parseHTML('<img>')).attr('src', event.target.result).appendTo(placeToInsertImagePreview);
                }

                reader.readAsDataURL(input.files[i]);
            }
        }

    };

    $('#photo_uploading').on('change', function() {
        imagesPreview(this, 'div.gallery');

    });

    $('#photo_uploading').on('change', function() {
        imagesPreview(this, 'div.new_gallery');
    });


});


$(function(){
    $("#message").delay(5000).slideUp(300);
});