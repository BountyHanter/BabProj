document.addEventListener("DOMContentLoaded", function() {
    $('.go_application').on('click', function() {
        $('.not_application').hide();
        $('.application').css('display', 'flex');
    });
    $('.modal').on('click', function(e) {
        var content = $(this).find('.modal_content');
		if(!content.is(e.target) && content.has(e.target).length === 0) {
			$('.modal').hide();
		}
    });
    $('.close').on('click', function() {
        $('.modal').hide();
    });
    $('.close_message').on('click', function() {
        $('.modal_message').fadeOut(300);
    });
    $('.creating_report_btn').on('click', function() {
        $('.modal_creating_report').show();
    });
    $('.send_check_btn').on('click', function() {
        $('.modal_send_check').show();
    });
    $('.tab_right_button').on('click', function() {
        $('.modal_request_withdrawal').show();
    });
    $('.color_select').on('change', function() {
        $(this).removeClass('blue green yellow g r purple');
        if($(this).val() == 'New'){$(this).addClass('blue');}
        if($(this).val() == 'Active'){$(this).addClass('green');}
        if($(this).val() == 'Processing'){$(this).addClass('yellow');}
        if($(this).val() == 'Completed'){$(this).addClass('g');}
        if($(this).val() == 'Canceled'){$(this).addClass('r');}
        if($(this).val() == 'Manual'){$(this).addClass('purple');}
    });
    $('.creating_report').on('change', 'input[type="checkbox"]', function() {
        if($(this).prop('checked')){
            $(this).parent().parent().css('opacity', '1');
        }else{
            $(this).parent().parent().css('opacity', '0.7');
        }
    });
    $('.modal_creating_report').on('change', 'input[type="checkbox"]', function() {
        if($(this).prop('checked')){
            $('.modal_creating_report .btn_b').css('opacity', '1');
            $('.modal_creating_report .btn_b').css('pointer-events', 'auto');
        }else{
            $('.modal_creating_report .btn_b').css('opacity', '0.5');
            $('.modal_creating_report .btn_b').css('pointer-events', 'none');
        }
    });
    $('.modal_creating_report a').on('click', function() {
        $('.modal').hide();
        $('.message_creating_report').show();
        setTimeout(() => {
            $('.modal_message').fadeOut(300);
        }, "2000");
    });
    $('.modal_send_check a').on('click', function() {
        $('.modal').hide();
        $('.message_check_successfully_uploaded').show();
        setTimeout(() => {
            $('.modal_message').fadeOut(300);
        }, "2000");
    });

    $('.copy').on('click', function() {
        GoCopy($(this).parent().find('input').val());
    });

    function GoCopy(selCopy){
        if (navigator.clipboard) {
            navigator.clipboard.writeText(selCopy).then(function() {
                console.log('Done!');
                /*$('.copied_mnemonic').fadeIn(300);
                setTimeout(() => {
                    $('.copied_mnemonic').fadeOut(300);
                }, "2000");*/
            }, function(err) {
                console.error('Failed... ', err);
            });
        } else {
            var inp = document.createElement('input');
            inp.value = selCopy;
            document.body.appendChild(inp);
            inp.select();
            if (document.execCommand('copy')) {
                console.log("Done!")
                /*$('.copied_mnemonic').fadeIn(300);
                setTimeout(() => {
                    $('.copied_mnemonic').fadeOut(300);
                }, "2000");*/
            } else {
                console.log("Failed...")
            }      
            document.body.removeChild(inp)
        }
    }
    /* dad */
    const dropFileZone = document.querySelector(".upload_zone_dragover")
    const statusText = document.getElementById("uploadForm_Hint")
    const uploadInput = document.querySelector(".form_upload_input")
    let setStatus = (text) => {
      statusText.textContent = text
    }
    const uploadUrl = "/upload";
    ["dragover", "drop"].forEach(function(event) {
      document.addEventListener(event, function(evt) {
        evt.preventDefault()
        return false
      })
    })
    dropFileZone.addEventListener("dragenter", function() {
      dropFileZone.classList.add("_active")
    })
    dropFileZone.addEventListener("dragleave", function() {
      dropFileZone.classList.remove("_active")
    })
    dropFileZone.addEventListener("drop", function() {
      dropFileZone.classList.remove("_active")
      const file = event.dataTransfer?.files[0]
      if (!file) {
        return
      }
      uploadInput.files = event.dataTransfer.files;
      $('.upload_zone_dragover > span').text(event.dataTransfer.files[0]['name']);
      processingUploadFile();
      /*if (file.type.startsWith("image/")) {
        uploadInput.files = event.dataTransfer.files
        processingUploadFile()
      } else {
        setStatus("Можно загружать только изображения")
        return false
      }*/
    })
    uploadInput.addEventListener("change", (event) => {
      const file = uploadInput.files?.[0]
      $('.upload_zone_dragover > span').text(file['name']);
      processingUploadFile()
      /*if (file && file.type.startsWith("image/")) {
        processingUploadFile()
      } else {
        setStatus("Можно загружать только изображения")
        return false
      }*/
    })
    function processingUploadFile(file) {
      if (file) {
        const dropZoneData = new FormData()
        const xhr = new XMLHttpRequest()
    
        dropZoneData.append("file", file)
    
        xhr.open("POST", uploadUrl, true)
    
        xhr.send(dropZoneData)
    
        xhr.onload = function () {
          if (xhr.status == 200) {
            setStatus("Всё загружено")
          } else {
            setStatus("Oшибка загрузки")
          }
          HTMLElement.style.display = "none"
        }
      }
    }
    function processingDownloadFileWithFetch() {
      fetch(url, {
        method: "POST",
      }).then(async (res) => {
        const reader = res?.body?.getReader();
        while (true && reader) {
          const { value, done } = await reader?.read()
          console.log("value", value)
          if (done) break
          console.log("Received", value)
        }
      })
    }
    /* /dad */
});